#!/usr/bin/env python3
"""
mlst_typing_setup.py - the optional "add your PubMLST key" setup of
mlst-typing (command line only; this file is not part of the Galaxy tool).

The database that ships with mlst-typing holds PubMLST data submitted up to
31 Dec 2024, which PubMLST gives without a login. Newer data needs the
user's own PubMLST account and key. This module

  - asks once, on the first run in a terminal: add a key, or skip;
  - takes either key PubMLST offers in the account profile:
      * the "Public data access key" (a personal API key, sent as the
        X-API-Key header), or
      * an OAuth client key + client secret (OAuth 1.0a, HMAC-SHA1; the
        user approves the tool once in the browser);
  - stores the key in the user's config folder (owner-only file);
  - builds the user's own database with mlst_typing_update.py, starting
    from a copy of the bundled one. Nothing is written to the bundled
    database or the repository.

mlst_typing.py calls first_run(), setup(), update() and remove(); it owns
the folder names and passes them in as `paths`. Standard library only.

For other programs (an app with its own "add your key" screen) nothing
here needs a terminal:
  - setup_with_key() takes the public data access key from a file or stdin
    (`mlst-typing --setup --key-file FILE|-`);
  - OAuth goes in two steps, because the user approves the tool in the
    browser in between: oauth_start() (`--setup --oauth-start --key-file
    FILE|-`, client key and client secret) prints the approval page as
    JSON and keeps the request token; oauth_finish() (`--setup
    --oauth-finish CODE`) takes the verification code PubMLST shows,
    saves the key and downloads;
  - check_newer() (`--update-check`, JSON) asks PubMLST whether any scheme
    changed since the own database was downloaded, without downloading;
  - status() feeds `mlst-typing --setup-status` (JSON), and --update /
    --setup --remove ask no questions.
"""

import base64
import datetime as dt
import getpass
import hashlib
import hmac
import json
import os
import secrets
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

EXE = "mlst-typing"
REST = "https://rest.pubmlst.org"
WEB = "https://pubmlst.org/bigsdb"
# PubMLST accounts are site-wide; the sign-in goes through one database.
AUTH_DB = "pubmlst_neisseria_seqdef"
CHECK_PATH = f"/db/{AUTH_DB}/schemes/1"      # scheme used to test a new key
ONLY_ENV = "MLST_TYPING_SETUP_ONLY"         # testing: comma-separated schemes
USER_AGENT = "mlst-typing-setup"

INTRO = f"""
{EXE}: database setup (asked once)

The database that comes with this tool holds PubMLST data submitted up to
31 December 2024. That part is free and needs no account.

For an up-to-date database (alleles and STs from 2025 on) PubMLST asks
every user to have their own account and key:
  1. Make a free account at https://pubmlst.org and accept its terms.
  2. In your account profile, create a key. Either kind works here:
       - the "Public data access key" (one key, the simple way), or
       - an OAuth key (a client key and a client secret).
  3. Paste it here. With an OAuth key you also approve the tool once in
     your browser.
The tool then downloads the current schemes to this computer (about 1.5
hours, once) and uses them from then on. Your key stays on this computer.

  [A] Add my key now
  [S] Skip: use the built-in free database (data to 31 Dec 2024).
      You can add a key any time later with:  {EXE} --setup
"""


class SetupError(Exception):
    pass


# --------------------------------------------------------------------------
# Talking to the user (stderr, so a report on stdout stays clean)
# --------------------------------------------------------------------------

def say(*text):
    print(*text, file=sys.stderr, flush=True)


def ask(prompt, hidden=False):
    """One line from the keyboard; '' on end of input."""
    if hidden:
        return getpass.getpass(prompt, stream=sys.stderr).strip()
    sys.stderr.write(prompt)
    sys.stderr.flush()
    return sys.stdin.readline().strip()


def choose(prompt, options):
    """Ask until the answer starts with one of the option letters; end of
    input counts as the last option."""
    while True:
        sys.stderr.write(prompt)
        sys.stderr.flush()
        line = sys.stdin.readline()
        if not line:
            return options[-1]
        if line.strip()[:1].lower() in options:
            return line.strip()[:1].lower()


def interactive():
    return sys.stdin.isatty() and sys.stderr.isatty()


# --------------------------------------------------------------------------
# Saved state: setup.json (the answer) and credentials.json (the key)
# --------------------------------------------------------------------------

def _state_file(paths):
    return os.path.join(paths["config"], "setup.json")


def _cred_file(paths):
    return os.path.join(paths["config"], "credentials.json")


def answered(paths):
    return os.path.exists(_state_file(paths))


def save_answer(paths, answer):
    os.makedirs(paths["config"], mode=0o700, exist_ok=True)
    with open(_state_file(paths), "w") as fh:
        json.dump({"answer": answer, "date": dt.date.today().isoformat()}, fh)
        fh.write("\n")


def _pending_file(paths):
    """The request token of an OAuth sign-in waiting for its code."""
    return os.path.join(paths["config"], "oauth_pending.json")


def _save_private(paths, path, data):
    """Owner-only file (mode 600) in an owner-only folder."""
    os.makedirs(paths["config"], mode=0o700, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as fh:
        json.dump(data, fh, indent=1)
        fh.write("\n")
    os.chmod(path, 0o600)


def _load(path):
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def save_credentials(paths, cred):
    _save_private(paths, _cred_file(paths), cred)


def load_credentials(paths):
    return _load(_cred_file(paths))


# --------------------------------------------------------------------------
# OAuth 1.0a (RFC 5849), HMAC-SHA1, parameters in the query string
# --------------------------------------------------------------------------

def pct(text):
    return urllib.parse.quote(str(text), safe="-._~")


def oauth_url(method, url, client_key, client_secret, token="", token_secret="",
              extra=None, nonce=None, timestamp=None):
    """url with the OAuth parameters and signature added to its query."""
    parts = urllib.parse.urlsplit(url)
    base = f"{parts.scheme}://{parts.netloc}{parts.path}"
    params = dict(urllib.parse.parse_qsl(parts.query, keep_blank_values=True))
    params.update(extra or {})
    params.update(oauth_consumer_key=client_key,
                  oauth_nonce=nonce or secrets.token_hex(16),
                  oauth_signature_method="HMAC-SHA1",
                  oauth_timestamp=str(timestamp or int(time.time())),
                  oauth_version="1.0")
    if token:
        params["oauth_token"] = token
    norm = "&".join(f"{pct(k)}={pct(v)}" for k, v in sorted(params.items()))
    base_string = "&".join((method.upper(), pct(base), pct(norm)))
    key = f"{pct(client_secret)}&{pct(token_secret)}"
    digest = hmac.new(key.encode(), base_string.encode(), hashlib.sha1).digest()
    params["oauth_signature"] = base64.b64encode(digest).decode()
    return base + "?" + "&".join(f"{pct(k)}={pct(v)}" for k, v in sorted(params.items()))


def get_json(url, headers=None, what="PubMLST"):
    """JSON reply of url. Errors never show the url (it carries the key)."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            detail = json.loads(e.read().decode("utf-8")).get("message", "")
        except Exception:  # noqa: BLE001
            detail = ""
        raise SetupError(f"{what} answered HTTP {e.code}"
                         + (f": {detail}" if detail else "")) from e
    except (urllib.error.URLError, OSError, ValueError) as e:
        raise SetupError(f"could not reach {what}: {e}") from e


def _token_pair(reply, what):
    try:
        return reply["oauth_token"], reply["oauth_token_secret"]
    except (KeyError, TypeError):
        raise SetupError(f"{what}: unexpected reply from PubMLST") from None


def oauth_session(cred):
    """New 12-hour session token from the lasting access token."""
    url = oauth_url("GET", f"{REST}/db/{AUTH_DB}/oauth/get_session_token",
                    cred["client_key"], cred["client_secret"],
                    cred["access_token"], cred["access_secret"])
    cred["session_token"], cred["session_secret"] = _token_pair(
        get_json(url, what="PubMLST (session token)"), "session token")
    return cred


def oauth_request(client_key, client_secret):
    """Sign-in, step 1: a request token, its secret and the page where the
    user approves the tool."""
    url = oauth_url("GET", f"{REST}/db/{AUTH_DB}/oauth/get_request_token",
                    client_key, client_secret, extra={"oauth_callback": "oob"})
    req_token, req_secret = _token_pair(
        get_json(url, what="PubMLST (client key)"), "request token")
    page = f"{WEB}?db={AUTH_DB}&page=authorizeClient&oauth_token={req_token}"
    return req_token, req_secret, page


def oauth_access(client_key, client_secret, req_token, req_secret, code):
    """Sign-in, step 2: the verification code -> access token -> session."""
    if not code:
        raise SetupError("no verification code given")
    url = oauth_url("GET", f"{REST}/db/{AUTH_DB}/oauth/get_access_token",
                    client_key, client_secret, req_token, req_secret,
                    extra={"oauth_verifier": code})
    acc_token, acc_secret = _token_pair(
        get_json(url, what="PubMLST (verification code)"), "access token")
    return oauth_session(dict(type="oauth", client_key=client_key,
                              client_secret=client_secret,
                              access_token=acc_token, access_secret=acc_secret))


def oauth_sign_in(client_key, client_secret):
    """Request token -> approval in the browser -> access token -> session."""
    req_token, req_secret, page = oauth_request(client_key, client_secret)
    say("\nOpen this page in your browser, log in to PubMLST and approve the tool:\n\n"
        f"  {page}\n\n"
        "PubMLST then shows a verification code.")
    code = ask("Verification code: ")
    return oauth_access(client_key, client_secret, req_token, req_secret, code)


# --------------------------------------------------------------------------
# Signers: what mlst_typing_update.http_get() uses for PubMLST requests
# --------------------------------------------------------------------------

class KeySigner:
    """Public data access key: one header, nothing to renew."""

    def __init__(self, cred):
        self.cred = cred

    @staticmethod
    def wants(url):
        return url.startswith(REST + "/")

    def apply(self, url):
        return url, {"X-API-Key": self.cred["key"]}

    def renew(self):
        raise RuntimeError("PubMLST refused the key")


class OAuthSigner(KeySigner):
    """OAuth: every request signed with the session token (renewed on 401)."""

    def __init__(self, cred, paths=None):
        super().__init__(cred)
        self.paths = paths

    def apply(self, url):
        c = self.cred
        return oauth_url("GET", url, c["client_key"], c["client_secret"],
                         c["session_token"], c["session_secret"]), {}

    def renew(self):
        try:
            oauth_session(self.cred)
        except SetupError as e:
            raise RuntimeError(str(e)) from e
        if self.paths:
            save_credentials(self.paths, self.cred)


def signer_for(cred, paths=None):
    return OAuthSigner(cred, paths) if cred.get("type") == "oauth" else KeySigner(cred)


def check_key(signer):
    """Ask PubMLST for one scheme with the key. Returns True when the reply
    no longer says the data is restricted to 31 Dec 2024."""
    url, headers = signer.apply(REST + CHECK_PATH)
    info = get_json(url, headers, what="PubMLST")
    return "restricted" not in str(info.get("message", ""))


# --------------------------------------------------------------------------
# The user's own database
# --------------------------------------------------------------------------

def have_own(paths):
    return os.path.exists(os.path.join(paths["db"], "blast", "mlst.fa.nsq"))


def build(paths, bundled, signer):
    """Build or refresh the own database. Returns True when it changed.

    Works on a copy (<db>.new) and swaps it in at the end, so a stopped or
    failed download leaves the database in use untouched. A scheme that
    fails, or that the account may not read, keeps the copy it had.
    """
    import mlst_typing_update as up

    if shutil.which("makeblastdb") is None:
        raise SetupError("makeblastdb not found - please install BLAST+")
    target, work = paths["db"], paths["db"] + ".new"
    source = target if have_own(paths) else bundled
    if not os.path.exists(os.path.join(source, "schemes.tsv")):
        raise SetupError(f"no scheme list (schemes.tsv) in {source}")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    shutil.rmtree(work, ignore_errors=True)
    say(f"Copying the database to work on ({source})")
    shutil.copytree(source, work)

    argv = ["--db", work, "--source", "pubmlst", "--version-label",
            f"PubMLST_{dt.date.today().isoformat()} (own account)"]
    if os.environ.get(ONLY_ENV):
        argv += ["--only", os.environ[ONLY_ENV]]
    say("Downloading the PubMLST schemes with your key. This takes a while;\n"
        "the database in use is not touched until the download is complete.")
    up.SIGNER = signer
    try:
        code = up.main(argv)
    except BaseException:
        shutil.rmtree(work, ignore_errors=True)
        raise
    finally:
        up.SIGNER = None
    if code == up.NO_CHANGES:
        shutil.rmtree(work, ignore_errors=True)
        return False
    if code != 0:
        shutil.rmtree(work, ignore_errors=True)
        raise SetupError(f"the database update failed (exit code {code})")
    shutil.rmtree(target, ignore_errors=True)
    os.replace(work, target)
    return True


def report(paths):
    """How many PubMLST schemes now hold data newer than the free set."""
    full = free = 0
    try:
        with open(os.path.join(paths["db"], "manifest.tsv")) as fh:
            header = fh.readline().rstrip("\n").split("\t")
            for line in fh:
                row = dict(zip(header, line.rstrip("\n").split("\t")))
                if row.get("source") != "pubmlst":
                    continue
                if row.get("restricted") == "True":
                    free += 1
                else:
                    full += 1
    except OSError:
        return
    say(f"PubMLST schemes with current data: {full}. Still the free data "
        f"(to 31 Dec 2024): {free}.")
    if free:
        say("For those, PubMLST did not give your account newer data (the "
            "account may need to be\nregistered with that species database "
            f"on pubmlst.org). Run '{EXE} --update' to try again.")


def download(paths, bundled, signer):
    changed = build(paths, bundled, signer)
    if changed:
        say(f"\nDone. Your own database is in {paths['db']}\n"
            f"and {EXE} uses it from now on. Refresh it with: {EXE} --update")
        report(paths)
    elif have_own(paths):
        say("\nYour own database is already up to date.")
    else:
        say("\nPubMLST gave nothing newer than the built-in database, so the "
            "built-in one stays in use.")
    return changed


# --------------------------------------------------------------------------
# The steps mlst_typing.py calls
# --------------------------------------------------------------------------

def add_key(paths, bundled):
    """Ask for the key, test it, save it and download the own database."""
    say("\nWhich key do you have?\n"
        "  [1] Public data access key (one key)\n"
        "  [2] OAuth key (client key and client secret)")
    kind = choose("Your choice [1/2]: ", ("1", "2"))
    if kind == "1":
        key = ask("Public data access key (not shown): ", hidden=True)
        if not key:
            raise SetupError("no key given")
        cred = dict(type="apikey", key=key)
    else:
        client_key = ask("Client key: ")
        client_secret = ask("Client secret (not shown): ", hidden=True)
        if not client_key or not client_secret:
            raise SetupError("client key and client secret are both needed")
        cred = oauth_sign_in(client_key, client_secret)
    use_key(paths, bundled, cred, questions=True)


def use_key(paths, bundled, cred, questions):
    """Test the key, save it, download. Without questions (key from a file)
    a key that does not unlock newer data is an error and is not saved."""
    signer = signer_for(cred, paths)
    say("Testing the key with PubMLST ...")
    if check_key(signer):
        say("The key works: PubMLST gives the full, current data.")
    else:
        limited = ("PubMLST accepted the key but still says the data is limited "
                   "to 31 December 2024")
        if not questions:
            raise SetupError(limited + "; key not saved")
        say(limited + ".\nThe download would most likely give the same data as "
            "the built-in database."
            + ("\nAn OAuth key (choice 2) may give more."
               if cred.get("type") == "apikey" else ""))
        if choose("Save this key and download anyway? [y/N]: ", ("y", "n")) != "y":
            raise SetupError("key not saved")
    save_credentials(paths, cred)
    save_answer(paths, "key")
    say(f"Key saved in {_cred_file(paths)} (readable only by you).")
    download(paths, bundled, signer)


def first_run(paths, bundled):
    """The one-time question. Never raises: typing carries on afterwards."""
    say(INTRO)
    try:
        if choose("Your choice [A/S]: ", ("a", "s")) == "s":
            save_answer(paths, "skipped")
            say(f"Skipped. Using the built-in database. Add a key later with: {EXE} --setup\n")
            return
        add_key(paths, bundled)
    except KeyboardInterrupt:
        say(f"\nStopped. Using the built-in database. Run '{EXE} --setup' to try again.\n")
    except (SetupError, RuntimeError, OSError) as e:
        say(f"\nSetup did not finish: {e}\n"
            f"Using the database already in place. Run '{EXE} --setup' to try again.\n")
    if not answered(paths):
        save_answer(paths, "not finished")
    say("")


def setup(paths, bundled):
    """--setup: the same question again, any time."""
    if not interactive():
        raise SetupError("--setup asks questions and needs a terminal")
    say(INTRO)
    cred = load_credentials(paths)
    if cred:
        say("A key is already saved; adding one replaces it.\n")
    if choose("Your choice [A/S]: ", ("a", "s")) == "s":
        if not cred:
            save_answer(paths, "skipped")
        say("Nothing changed." if cred else "Skipped. Using the built-in database.")
        return 0
    add_key(paths, bundled)
    return 0


def _key_words(key_file):
    """The words in a key file ('-' = stdin). Keys never come from the
    command line, where other users of the computer could see them."""
    try:
        if key_file == "-":
            text = sys.stdin.read()
        else:
            with open(key_file) as fh:
                text = fh.read()
    except OSError as e:
        raise SetupError(f"could not read the key: {e}") from e
    return text.split()


def setup_with_key(paths, bundled, key_file):
    """--setup --key-file FILE|-: the public data access key from a file or
    stdin, no questions (for apps and scripts)."""
    words = _key_words(key_file)
    if len(words) != 1:
        raise SetupError("the key file must hold the public data access key and nothing else")
    use_key(paths, bundled, dict(type="apikey", key=words[0]), questions=False)
    return 0


def oauth_start(paths, key_file):
    """--setup --oauth-start --key-file FILE|-: OAuth without a terminal,
    step 1. The file holds the client key, then the client secret. Prints
    the page the user must open as JSON and keeps the request token for
    oauth_finish(). Nothing is saved as the key yet."""
    words = _key_words(key_file)
    if len(words) != 2:
        raise SetupError("the key file must hold the client key, then the client "
                         "secret, and nothing else")
    req_token, req_secret, page = oauth_request(*words)
    _save_private(paths, _pending_file(paths),
                  dict(client_key=words[0], client_secret=words[1],
                       request_token=req_token, request_secret=req_secret))
    print(json.dumps({"approve_url": page}, indent=1))
    return 0


def oauth_finish(paths, bundled, code):
    """--setup --oauth-finish CODE: OAuth without a terminal, step 2. CODE
    is the verification code PubMLST showed after the approval. Saves the
    key and downloads, like setup_with_key(). A wrong code keeps the
    request token, so the code can be given again."""
    pending = _load(_pending_file(paths))
    if not pending:
        raise SetupError(f"no OAuth sign-in is waiting for a code - start with "
                         f"'{EXE} --setup --oauth-start --key-file FILE'")
    cred = oauth_access(pending["client_key"], pending["client_secret"],
                        pending["request_token"], pending["request_secret"],
                        code.strip())
    os.remove(_pending_file(paths))
    use_key(paths, bundled, cred, questions=False)
    return 0


def status(paths):
    """Where setup stands, for --setup-status. Never includes the key."""
    answer = (_load(_state_file(paths)) or {}).get("answer", "")
    cred = load_credentials(paths) or {}
    return {"asked": bool(answer), "answer": answer,
            "key_saved": bool(cred), "key_type": cred.get("type", ""),
            "oauth_waiting_for_code": os.path.exists(_pending_file(paths)),
            "own_database": have_own(paths), "own_database_folder": paths["db"],
            "config_folder": paths["config"]}


def _signer_ready(paths):
    cred = load_credentials(paths)
    if not cred:
        raise SetupError(f"no PubMLST key saved yet - run '{EXE} --setup' first")
    signer = signer_for(cred, paths)
    if cred.get("type") == "oauth":
        signer.renew()
    return signer


def check_newer(paths, bundled):
    """--update-check: does PubMLST hold anything newer than the database
    in use (the own one, or the bundled one before the first download)?
    Asks each scheme for its date of last change with the saved key and
    downloads no data. Prints JSON; the scheme count goes to stderr."""
    import mlst_typing_update as up

    signer = _signer_ready(paths)
    source = paths["db"] if have_own(paths) else bundled
    have = up.read_manifest(os.path.join(source, "manifest.tsv"))
    rows = [r for r in up.read_scheme_list(os.path.join(source, "schemes.tsv"))
            if up.folder_of(r["source"]) == "pubmlst"]
    if os.environ.get(ONLY_ENV):
        only = set(os.environ[ONLY_ENV].split(","))
        rows = [r for r in rows if r["scheme"] in only]
    newer, failed = [], []
    up.SIGNER = signer
    try:
        for i, row in enumerate(rows, 1):
            name = row["scheme"]
            say(f"[{i}/{len(rows)}] {name}")
            try:
                info = up.http_json(row["api"].rstrip("/"))
            except (RuntimeError, ValueError):
                failed.append(name)
                continue
            message = str(info.get("message", ""))
            limited = "restricted" in message or "2024-12-31" in message
            old = have.get(name)
            if (old is None
                    or (old.get("restricted") == "True" and not limited)
                    or str(info.get("last_updated", "")) > old.get("last_updated", "")):
                newer.append(name)
    finally:
        up.SIGNER = None
    print(json.dumps({"newer": bool(newer), "schemes_newer": newer,
                      "schemes_checked": len(rows) - len(failed),
                      "schemes_failed": failed,
                      "database": source,
                      "database_version": " + ".join(x for x in up.read_version(source) if x)},
                     indent=1))
    return 0


def update(paths, bundled):
    """--update: refresh the own database with the saved key."""
    download(paths, bundled, _signer_ready(paths))
    return 0


def remove(paths):
    """--setup --remove: forget the key and the own database."""
    gone = []
    if os.path.exists(_pending_file(paths)):
        os.remove(_pending_file(paths))
    if os.path.exists(_cred_file(paths)):
        os.remove(_cred_file(paths))
        gone.append("the saved key")
    for folder in (paths["db"], paths["db"] + ".new"):
        if os.path.isdir(folder):
            shutil.rmtree(folder)
            gone.append(folder)
    save_answer(paths, "skipped")
    say(("Removed: " + ", ".join(gone) + ".") if gone else "Nothing to remove.",
        f"The built-in database is used. Add a key again with: {EXE} --setup")
    return 0
