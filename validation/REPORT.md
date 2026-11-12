# Validation, database PubMLST_2026-11 + EnteroBase_2026-11-11

Run 2026-11-11: 194 genomes listed (one public NCBI assembly per scheme + priority organisms + matched genomes).

- Typed: 194 (0 without a genome)
- Called the scheme the genome was picked for: 151/194
- Full ST (PERFECT or MULTICOPY): 146/194
- Same result as upstream mlst on the same database: **176/194**
- Upstream picked another of the tied schemes this run: 13/194 (see Ties)
- Deliberate differences (identical copies of a locus, locus names mlst cannot read): 5/194 (see Deliberate differences)
- Real differences: **0/194**

## Priority organisms

| Genome | Scheme | ST | Alleles | Status | Score | Warnings |
|---|---|---|---|---|---|---|
| Streptococcus pyogenes (Group A Strep) SF370 (GCF_000006785.2) | spyogenes | 28 | gki(4);gtr(3);murI(4);mutS(4);recP(4);xpt(2);yqiL(4) | PERFECT | 100 | none |
| Neisseria gonorrhoeae FA 1090 (GCF_000006845.1) | neisseria | 1899 | abcZ(109);adk(39);aroE(67);fumC(190);gdh(147);pdhC(71);pgm(65) | PERFECT | 100 | none |
| Salmonella enterica Typhimurium LT2 (GCF_000006945.2) | salmonella | 19 | aroC(10);dnaN(7);hemD(12);hisD(9);purE(5);sucA(9);thrA(2) | PERFECT | 100 | none |
| Shigella sonnei Ss046 (GCF_000092525.1) | ecoli_achtman_4 | 152 | adk(11);fumC(63);gyrB(7);icd(1);mdh(14);purA(7);recA(7) | PERFECT | 100 | none |
| Shigella flexneri 2a 301 (GCF_000006925.2) | ecoli_achtman_4 | 245 | adk(6);fumC(61);gyrB(6);icd(11);mdh(13);purA(3);recA(50) | PERFECT | 100 | none |
| Mycobacterium tuberculosis H37Rv (GCF_000195955.2) | mycobacteria_2 | 215 | S14Z(17);L35(15);S19(20);L19(19);S12(20);S8(18);L16(22);S7(19) | PERFECT | 100 | none |

## Matched genomes for schemes whose first NCBI pick did not type (26)

Some schemes cover a whole genus, and the first NCBI pick was a species the scheme does not cover, so it typed NONE or BAD. Those first picks stay in the tables below: they show mlst-typing and mlst agree there too. Here each of those schemes gets a genome of a species it does cover. "ST in this scheme" is the ST the scheme gives; "(tie)" means another scheme with the same score is reported first and this scheme's ST is in Warnings.

| Scheme | First pick: result | Matched genome | Called scheme | ST in this scheme | Status | Score | Same as mlst | Warnings | Note |
|---|---|---|---|---|---|---|---|---|---|
| arcobacter | Arcobacter acticola: NONE | Aliarcobacter butzleri 6V (GCF_004283115.1) | arcobacter | 537 | PERFECT | 100 | yes | none | A. butzleri, the main species of the scheme |
| brachyspira | Brachyspira aalborgi: NONE | Brachyspira hyodysenteriae ATCC 27164 (GCF_001676785.2) | brachyspira | 5 | PERFECT | 100 | tie | TIE: brachyspira (ST5), brachyspira_2 (ST56) | B. hyodysenteriae (genus-wide scheme) |
| brachyspira_2 | Brachyspira aalborgi: NONE | Brachyspira hyodysenteriae BH718 (GCF_002850235.1) | brachyspira_2 | 83 | PERFECT | 100 | yes | none | scheme is B. hyodysenteriae MLST |
| brachyspira_3 | Brachyspira aalborgi: NONE | Brachyspira intermedia PWS/A (GCF_000223215.1) | brachyspira_3 | - | NOVEL | 90 | yes | none | scheme is B. intermedia MLST; all alleles exact, combination has no ST yet |
| brachyspira_4 | Brachyspira aalborgi: NONE | Brachyspira pilosicoli 95/1000 (GCF_000143725.1) | brachyspira_4 | 138 | PERFECT | 100 | yes | none | scheme is B. pilosicoli MLST |
| brachyspira_5 | Brachyspira aalborgi: NONE | Brachyspira hampsonii 30446 (GCF_000316195.1) | brachyspira_5 | 7 | PERFECT | 100 | yes | none | scheme is B. hampsonii MLST |
| halobacteria | Candidatus Halobonum tyrrellensis G22: NONE | Halorubrum lacusprofundi ATCC 49239 (GCF_000022205.1) | halobacteria | - | NOVEL | 90 | no (deliberate, see below) | none | Halorubrum; the scheme has no public ST profiles, so no ST is possible |
| leptospira | Leptospira abararensis: NONE | Leptospira interrogans serovar Copenhageni FDAARGOS_203 (GCF_002073495.2) | leptospira | 17 | PERFECT | 100 | yes | TIE: leptospira (ST17), leptospira_2 (ST47), leptospira_3 (ST2) | L. interrogans |
| leptospira_2 | Leptospira abararensis: NONE | Leptospira interrogans serovar Copenhageni FDAARGOS_203 (GCF_002073495.2) | leptospira | 47 (tie) | PERFECT | 100 | tie | TIE: leptospira (ST17), leptospira_2 (ST47), leptospira_3 (ST2) | L. interrogans |
| leptospira_3 | Leptospira abararensis: NONE | Leptospira interrogans CUDO5 (GCF_002370085.3) | leptospira | 188 (tie) | PERFECT | 100 | tie | TIE: leptospira (ST26), leptospira_3 (ST188) | L. interrogans |
| liberibacter | Candidatus Liberibacter africanus PTSAPSY: NONE | Candidatus Liberibacter solanacearum CLso-ZC1 (GCF_000183665.1) | liberibacter | 10 | PERFECT | 100 | yes | none | Ca. L. solanacearum |
| mycobacteria_2 | Candidatus Mycobacterium methanotrophicum: NONE | Mycobacterium tuberculosis H37Rv (GCF_000195955.2) | mycobacteria_2 | 215 | PERFECT | 100 | yes | none | M. tuberculosis (same genome as the priority list) |
| providencia | Candidatus Providencia siddallii: NONE | Providencia stuartii 41 (GCF_035747985.1) | providencia | 233 | PERFECT | 100 | yes | none | P. stuartii |
| rhodococcus | Rhodococcus (subgen. Prescottella) agglutinans: NONE | Rhodococcus (Prescottella) equi WY (GCF_007197835.1) | rhodococcus | 36 | PERFECT | 100 | yes | none | R. equi |
| serratia | Serratia aquatilis: NONE | Serratia marcescens ELP1.10 (GCF_030291735.1) | serratia | 1305 | PERFECT | 100 | yes | none | S. marcescens |
| shewanella | Shewanella abyssi: NONE | Shewanella algae MARS 14 (GCF_000947195.1) | shewanella | 26 | PERFECT | 100 | yes | none | S. algae |
| sinorhizobium | Sinorhizobium alkalisoli: NONE | Sinorhizobium (Ensifer) meliloti MABNR56 (GCF_037023865.1) | sinorhizobium | 9 | PERFECT | 100 | yes | none | S. meliloti |
| streptomyces | Candidatus Streptomyces philanthi: NONE | Streptomyces griseus NRRL B-2165 (GCF_001723115.1) | streptomyces | 12 | PERFECT | 100 | yes | none | S. griseus |
| ureaplasma | Ureaplasma canigenitalium ATCC 51252: NONE | Ureaplasma parvum serovar 3 ATCC 27815 (GCF_000019345.1) | ureaplasma | 2 | PERFECT | 100 | yes | none | U. parvum |
| vibrio | Vibrio aerogenes: NONE | Vibrio parahaemolyticus RIMD 2210633 (GCF_000196095.1) | vibrio | 152 | PERFECT | 100 | tie | TIE: vibrio (ST152), vparahaemolyticus (ST3) | V. parahaemolyticus (same genome as picked for vparahaemolyticus) |
| vtapetis | Vibrio tapetis subsp. quintayensis: NONE | Vibrio tapetis subsp. tapetis (GCF_900233005.1) | vtapetis | - | PARTIAL | 81 | yes | none | V. tapetis subsp. tapetis; closest public genome, 8 of 10 loci exact |
| wolbachia | Candidatus Wolbachia massiliensis: NONE | Wolbachia endosymbiont of Drosophila melanogaster wMelPlus (GCF_947533255.1) | wolbachia | 1 | PERFECT | 100 | yes | none | Wolbachia wMel |
| aeromonas | Aeromonas allosaccharophila: BAD | Aeromonas hydrophila subsp. hydrophila ATCC 7966 (GCF_000014805.1) | aeromonas | 1 | PERFECT | 100 | yes | none | A. hydrophila |
| pdamselae | Photobacterium damselae subsp. damselae: BAD | Photobacterium damselae subsp. piscicida AS-16-0555-7 (GCF_014775695.1) | pdamselae | 46 | PERFECT | 100 | yes | none | P. damselae subsp. piscicida |
| scanis | Streptococcus equinus: BAD | Streptococcus canis NCTC12191 (GCF_900636575.1) | scanis | 9 | PERFECT | 100 | yes | none | S. canis |
| smaltophilia | Stenotrophomonas acidaminiphila: BAD | Stenotrophomonas maltophilia ISMMS3 (GCF_001274595.1) | smaltophilia | 280 | PERFECT | 100 | yes | none | S. maltophilia |

## EnteroBase cross-check (174 genomes)

Every genome is typed against PubMLST and, separately, against the EnteroBase schemes. PubMLST is the main source; the EnteroBase row is reported only when PubMLST has no ST and EnteroBase has one. The case numbers are those of the README section "How to read the report".

| Case | What happened | Genomes |
|---|---|---|
| 1 | PubMLST ST, EnteroBase has no scheme for it | 125 |
| 2 | PubMLST ST, EnteroBase same scheme and same ST | 7 |
| 3 | PubMLST ST, EnteroBase same scheme but another ST | 0 |
| 4 | PubMLST ST, EnteroBase same scheme without an ST | 0 |
| 5 | PubMLST ST, EnteroBase finds a different scheme | 2 |
| 6 | no PubMLST ST, EnteroBase ST (EnteroBase row reported) | 0 |
| 7 | no PubMLST scheme, EnteroBase ST (EnteroBase row reported) | 0 |
| 8 | no ST in either, both find a scheme | 0 |
| 9 | no PubMLST ST, EnteroBase has no scheme for it | 24 |
| 10 | no PubMLST scheme, EnteroBase scheme without an ST | 0 |
| 11 | no scheme in either | 16 |

Genomes where EnteroBase finds a scheme (9):

| Genome | Case | PubMLST | EnteroBase | Row reported | Warnings in the report |
|---|---|---|---|---|---|
| Escherichia coli O157:H7 str. Sakai (GCF_000008865.2) | 2 | ecoli_achtman_4 ST11, PERFECT | ecoli_achtman_enterobase ST11, PERFECT | PubMLST | none |
| Klebsiella pneumoniae subsp. pneumoniae HS11286 (GCF_000240185.1) | 2 | ecoli_achtman_4 ST14464, PERFECT | ecoli_achtman_enterobase ST14464, PERFECT | PubMLST | TIE: ecoli_achtman_4 (ST14464), klebsiella (ST11) |
| Moraxella catarrhalis (GCF_900476075.1) | 2 | mcatarrhalis_achtman_6 ST54, PERFECT | mcatarrhalis_achtman_enterobase ST54, PERFECT | PubMLST | none |
| Salmonella enterica subsp. enterica serovar Typhimurium str. LT2 (GCF_000006945.2) | 2 | salmonella ST19, PERFECT | senterica_achtman_enterobase ST19, PERFECT | PubMLST | none |
| Yersinia aldovae 670-83 (GCF_000834395.1) | 5 | ypseudotuberculosis_achtman_3 ST217, PERFECT | yersinia_mcnally_enterobase ST177, PERFECT | PubMLST | none |
| Yersinia pseudotuberculosis (GCF_900637475.1) | 5 | yersinia ST90, PERFECT | ypseudotuberculosis_achtman_enterobase ST9, PERFECT | PubMLST | TIE: yersinia (ST90), ypseudotuberculosis_achtman_3 (ST9) |
| Yersinia ruckeri (GCF_017498685.1) | 2 | yersinia ST44, PERFECT | yersinia_mcnally_enterobase ST44, PERFECT | PubMLST | TIE: yersinia (ST44), ypseudotuberculosis_achtman_3 (ST276), yruckeri (ST33) |
| Shigella sonnei Ss046 (GCF_000092525.1) | 2 | ecoli_achtman_4 ST152, PERFECT | ecoli_achtman_enterobase ST152, PERFECT | PubMLST | none |
| Shigella flexneri 2a 301 (GCF_000006925.2) | 2 | ecoli_achtman_4 ST245, PERFECT | ecoli_achtman_enterobase ST245, PERFECT | PubMLST | none |

## Real differences from upstream mlst (0)

None.

## Deliberate differences from upstream mlst (5)

Two things mlst-typing does differently on purpose. (1) When a locus is in the genome in several copies of the same allele, e.g. `16S(1,1)`, mlst reports MIXED and no ST; mlst-typing keeps the copies in the allele column, looks up the ST and reports MULTICOPY. MIXED is kept for different alleles at one locus. (2) mlst cannot read locus names such as `EF-2` or `rpoB'` and reports those loci as missing; mlst-typing matches them.

| Genome | Why | mlst-typing | upstream mlst |
|---|---|---|---|
| Bartonella henselae (GCF_019930925.1) | identical copies of a locus: ST reported, MULTICOPY | bhenselae ST1: 16S(1,1);batR(1);ftsZ(1);gltA(1);groEL(1);nlpD(1);ribC(1);rpoB(1), MULTICOPY, score 100 | bhenselae ST-: 16S(1,1);batR(1);ftsZ(1);gltA(1);groEL(1);nlpD(1);ribC(1);rpoB(1), MIXED, score 90 |
| Candidatus Chlamydia corallus (GCF_002817655.1) | identical copies of a locus: ST reported, MULTICOPY | chlamydiales ST265: gatA(79);oppA(73);hflX(84);gidA(86);enoA(90);hemN(70,70);fumC(72), MULTICOPY, score 100 | chlamydiales ST-: gatA(79);oppA(73);hflX(84);gidA(86);enoA(90);hemN(70,70);fumC(72), MIXED, score 90 |
| Helicobacter cinaedi PAGU611 (GCF_000284635.1) | identical copies of a locus: ST reported, MULTICOPY | hcinaedi ST8: 23S_rRNA(3,3);ppa(4);aspA(4);aroE(3);atpA(2);tkt(3);cdtB(2), MULTICOPY, score 100 | hcinaedi ST-: 23S_rRNA(3,3);ppa(4);aspA(4);aroE(3);atpA(2);tkt(3);cdtB(2), MIXED, score 90 |
| Porphyromonas gingivalis ATCC 33277 (GCF_000010505.1) | identical copies of a locus: ST reported, MULTICOPY | pgingivalis ST96: ftsQ(5);gpdxJ(9);hagB(1,1);mcmA(1);pepO(1);pga(5);recA(5), MULTICOPY, score 100 | pgingivalis ST-: ftsQ(5);gpdxJ(9);hagB(1,1);mcmA(1);pepO(1);pga(5);recA(5), MIXED, score 90 |
| Halorubrum lacusprofundi ATCC 49239 (GCF_000022205.1) | locus names mlst cannot read | halobacteria ST-: atpB(4);EF-2(4);radA(4);rpoB'(3);secY(4), NOVEL, score 90 | halobacteria ST-: atpB(4);EF-2(-);radA(4);rpoB'(-);secY(4), MISSING, score 54 |

## Ties (same top score for more than one scheme) (15)

Two or more schemes give these genomes the same top score. Upstream mlst picks one of them at random (its answer can change from run to run); mlst-typing always reports the first by name and prints a warning listing the others in the WARNINGS column.

| Genome | mlst-typing reports | upstream mlst (this run) | Score | Warnings |
|---|---|---|---|---|
| Bacillus licheniformis (GCF_034478925.1) | blicheniformis_14 ST1 | bsubtilis ST29 | 100 | TIE: blicheniformis_14 (ST1), bsubtilis (ST29) |
| Corynebacterium diphtheriae (GCF_001457455.1) | cdiphtheriae ST26 | diphtheria_3 ST26 | 100 | TIE: cdiphtheriae (ST26), diphtheria_3 (ST26) |
| Klebsiella pneumoniae subsp. pneumoniae HS11286 (GCF_000240185.1) | ecoli_achtman_4 ST14464 | klebsiella ST11 | 100 | TIE: ecoli_achtman_4 (ST14464), klebsiella (ST11) |
| Mycobacteroides abscessus ATCC 19977 (GCF_000069185.1) | mabscessus ST5 | mabscessus ST5 | 100 | TIE: mabscessus (ST5), mycobacteria_2 (ST5) |
| Mycoplasmopsis bovis PG45 (GCF_000183385.1) | mbovis ST17 | mbovis_2 ST12 | 100 | TIE: mbovis (ST17), mbovis_2 (ST12) |
| Mycoplasmoides gallisepticum (GCF_900476085.1) | mgallisepticum ST23 | mgallisepticum ST23 | 100 | TIE: mgallisepticum (ST23), mgallisepticum_2 (ST1) |
| Pasteurella multocida (GCF_002073255.2) | pmultocida ST124 | pmultocida ST124 | 100 | TIE: pmultocida (ST124), pmultocida_2 (ST8) |
| Streptococcus gallolyticus (GCF_013267695.1) | sbsec ST34 | sgallolyticus ST117 | 100 | TIE: sbsec (ST34), sgallolyticus (ST117) |
| Vibrio parahaemolyticus RIMD 2210633 (GCF_000196095.1) | vibrio ST152 | vibrio ST152 | 100 | TIE: vibrio (ST152), vparahaemolyticus (ST3) |
| Vibrio vulnificus NBRC 15645 = ATCC 27562 (GCF_002224265.1) | vibrio ST126 | vvulnificus ST3 | 100 | TIE: vibrio (ST126), vvulnificus (ST3) |
| Yersinia pseudotuberculosis (GCF_900637475.1) | yersinia ST90 | yersinia ST90 | 100 | TIE: yersinia (ST90), ypseudotuberculosis_achtman_3 (ST9) |
| Yersinia ruckeri (GCF_017498685.1) | yersinia ST44 | yruckeri ST33 | 100 | TIE: yersinia (ST44), ypseudotuberculosis_achtman_3 (ST276), yruckeri (ST33) |
| Brachyspira hyodysenteriae ATCC 27164 (GCF_001676785.2) | brachyspira ST5 | brachyspira_2 ST56 | 100 | TIE: brachyspira (ST5), brachyspira_2 (ST56) |
| Leptospira interrogans serovar Copenhageni FDAARGOS_203 (GCF_002073495.2) | leptospira ST17 | leptospira ST17 | 100 | TIE: leptospira (ST17), leptospira_2 (ST47), leptospira_3 (ST2) |
| Leptospira interrogans CUDO5 (GCF_002370085.3) | leptospira ST26 | leptospira_3 ST188 | 100 | TIE: leptospira (ST26), leptospira_3 (ST188) |

## Other scheme called than the one picked for (43)

Each genome was picked from NCBI for one scheme, but typing chose another (or none). This is about the genome choice and overlapping schemes, not a disagreement between the tools.

| Picked for scheme | Genome | Called scheme | ST | Status | Why | Warnings |
|---|---|---|---|---|---|---|
| abaumannii | Acinetobacter baumannii (GCF_009035845.1) | abaumannii_2 | ST52 | PERFECT | `abaumannii` is skipped by default (`--exclude`), so the other scheme for this species is used |  |
| arcobacter | Arcobacter acticola (GCF_013177675.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Arcobacter acticola), so no scheme matches |  |
| brachyspira | Brachyspira aalborgi (GCF_008016755.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Brachyspira aalborgi), so no scheme matches |  |
| brachyspira_2 | Brachyspira aalborgi (GCF_008016755.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Brachyspira aalborgi), so no scheme matches |  |
| brachyspira_3 | Brachyspira aalborgi (GCF_008016755.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Brachyspira aalborgi), so no scheme matches |  |
| brachyspira_4 | Brachyspira aalborgi (GCF_008016755.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Brachyspira aalborgi), so no scheme matches |  |
| brachyspira_5 | Brachyspira aalborgi (GCF_008016755.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Brachyspira aalborgi), so no scheme matches |  |
| diphtheria_3 | Corynebacterium diphtheriae (GCF_001457455.1) | cdiphtheriae | ST26 | PERFECT | Tie with `diphtheria_3` (same score); the first by name is reported | TIE: cdiphtheriae (ST26), diphtheria_3 (ST26) |
| ecoli | Escherichia coli O157:H7 str. Sakai (GCF_000008865.2) | ecoli_achtman_4 | ST11 | PERFECT | `ecoli` is skipped by default (`--exclude`), so the other scheme for this species is used |  |
| halobacteria | Candidatus Halobonum tyrrellensis G22 (GCF_000495475.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Candidatus Halobonum tyrrellensis G22), so no scheme matches |  |
| klebsiella | Klebsiella pneumoniae subsp. pneumoniae HS11286 (GCF_000240185.1) | ecoli_achtman_4 | ST14464 | PERFECT | Tie with `klebsiella` (same score); the first by name is reported | TIE: ecoli_achtman_4 (ST14464), klebsiella (ST11) |
| leptospira | Leptospira abararensis (GCF_016918735.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Leptospira abararensis), so no scheme matches |  |
| leptospira_2 | Leptospira abararensis (GCF_016918735.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Leptospira abararensis), so no scheme matches |  |
| leptospira_3 | Leptospira abararensis (GCF_016918735.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Leptospira abararensis), so no scheme matches |  |
| liberibacter | Candidatus Liberibacter africanus PTSAPSY (GCF_001021085.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Candidatus Liberibacter africanus PTSAPSY), so no scheme matches |  |
| mbovis_2 | Mycoplasmopsis bovis PG45 (GCF_000183385.1) | mbovis | ST17 | PERFECT | Tie with `mbovis_2` (same score); the first by name is reported | TIE: mbovis (ST17), mbovis_2 (ST12) |
| mgallisepticum_2 | Mycoplasmoides gallisepticum (GCF_900476085.1) | mgallisepticum | ST23 | PERFECT | Tie with `mgallisepticum_2` (same score); the first by name is reported | TIE: mgallisepticum (ST23), mgallisepticum_2 (ST1) |
| mhominis_3 | Metamycoplasma hominis ATCC 27545 (GCF_000767725.1) | mhominis | - | NOVEL | `mhominis` scores higher than `mhominis_3` for this genome |  |
| mycobacteria_2 | Candidatus Mycobacterium methanotrophicum (GCF_023515995.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Candidatus Mycobacterium methanotrophicum), so no scheme matches |  |
| pdamselae | Photobacterium damselae subsp. damselae (GCF_038086725.1) | vibrio | - | BAD | `vibrio` scores higher than `pdamselae` for this genome |  |
| pmultocida_2 | Pasteurella multocida (GCF_002073255.2) | pmultocida | ST124 | PERFECT | Tie with `pmultocida_2` (same score); the first by name is reported | TIE: pmultocida (ST124), pmultocida_2 (ST8) |
| providencia | Candidatus Providencia siddallii (GCF_964026685.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Candidatus Providencia siddallii), so no scheme matches |  |
| rhodococcus | Rhodococcus (subgen. Prescottella) agglutinans (GCF_004011865.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Rhodococcus), so no scheme matches |  |
| scanis | Streptococcus equinus (GCF_049393805.1) | sbsec | - | BAD | `sbsec` scores higher than `scanis` for this genome |  |
| senterica_achtman_2 | Salmonella enterica subsp. enterica serovar Typhimurium str. LT2 (GCF_000006945.2) | salmonella | ST19 | PERFECT | `senterica_achtman_2` is skipped by default (`--exclude`), so the other scheme for this species is used |  |
| serratia | Serratia aquatilis (GCF_044865145.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Serratia aquatilis), so no scheme matches |  |
| sgallolyticus | Streptococcus gallolyticus (GCF_013267695.1) | sbsec | ST34 | PERFECT | Tie with `sgallolyticus` (same score); the first by name is reported | TIE: sbsec (ST34), sgallolyticus (ST117) |
| shewanella | Shewanella abyssi (GCF_023284025.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Shewanella abyssi), so no scheme matches |  |
| sinorhizobium | Sinorhizobium alkalisoli (GCF_008932245.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Sinorhizobium alkalisoli), so no scheme matches |  |
| sthermophilus | Streptococcus thermophilus (GCF_903886475.1) | streptothermophilus | ST59 | PERFECT | `streptothermophilus` scores higher than `sthermophilus` for this genome |  |
| streptomyces | Candidatus Streptomyces philanthi (GCF_059553635.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Candidatus Streptomyces philanthi), so no scheme matches |  |
| ureaplasma | Ureaplasma canigenitalium ATCC 51252 (GCF_000712165.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Ureaplasma canigenitalium ATCC 51252), so no scheme matches |  |
| vcholerae_2 | Vibrio cholerae IEC224 (GCF_000250855.1) | vcholerae | ST69 | PERFECT | `vcholerae_2` is skipped by default (`--exclude`), so the other scheme for this species is used |  |
| vibrio | Vibrio aerogenes (GCF_024346755.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Vibrio aerogenes), so no scheme matches |  |
| vparahaemolyticus | Vibrio parahaemolyticus RIMD 2210633 (GCF_000196095.1) | vibrio | ST152 | PERFECT | Tie with `vparahaemolyticus` (same score); the first by name is reported | TIE: vibrio (ST152), vparahaemolyticus (ST3) |
| vtapetis | Vibrio tapetis subsp. quintayensis (GCF_030409945.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Vibrio tapetis subsp. quintayensis), so no scheme matches |  |
| vvulnificus | Vibrio vulnificus NBRC 15645 = ATCC 27562 (GCF_002224265.1) | vibrio | ST126 | PERFECT | Tie with `vvulnificus` (same score); the first by name is reported | TIE: vibrio (ST126), vvulnificus (ST3) |
| wolbachia | Candidatus Wolbachia massiliensis (GCF_014771645.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Candidatus Wolbachia massiliensis), so no scheme matches |  |
| yersinia | Yersinia aldovae 670-83 (GCF_000834395.1) | ypseudotuberculosis_achtman_3 | ST217 | PERFECT | `ypseudotuberculosis_achtman_3` scores higher than `yersinia` for this genome |  |
| ypseudotuberculosis_achtman_3 | Yersinia pseudotuberculosis (GCF_900637475.1) | yersinia | ST90 | PERFECT | Tie with `ypseudotuberculosis_achtman_3` (same score); the first by name is reported | TIE: yersinia (ST90), ypseudotuberculosis_achtman_3 (ST9) |
| yruckeri | Yersinia ruckeri (GCF_017498685.1) | yersinia | ST44 | PERFECT | Tie with `yruckeri` (same score); the first by name is reported | TIE: yersinia (ST44), ypseudotuberculosis_achtman_3 (ST276), yruckeri (ST33) |
| leptospira_2 | Leptospira interrogans serovar Copenhageni FDAARGOS_203 (GCF_002073495.2) | leptospira | ST17 | PERFECT | Tie with `leptospira_2` (same score); the first by name is reported | TIE: leptospira (ST17), leptospira_2 (ST47), leptospira_3 (ST2) |
| leptospira_3 | Leptospira interrogans CUDO5 (GCF_002370085.3) | leptospira | ST26 | PERFECT | Tie with `leptospira_3` (same score); the first by name is reported | TIE: leptospira (ST26), leptospira_3 (ST188) |

## Schemes without a validation genome (0)

None.

## All genomes (174)

Each genome once, as `mlst-typing --full --combine-alleles --no-enterobase` reports it (the PubMLST result that is compared with mlst). What the normal report shows once EnteroBase is added is in "EnteroBase cross-check" above.

| Genome | Scheme | ST | Alleles | Status | Score | Warnings |
|---|---|---|---|---|---|---|
| Aggregatibacter actinomycetemcomitans (GCF_023518055.1) | aactinomycetemcomitans | - | adk(1);atpG(5);frdB(1);mdh(1);pgi(1);recA(~1);zwf(3) | PARTIAL | 86 | none |
| Acinetobacter baumannii (GCF_009035845.1) | abaumannii_2 | 52 | Pas_cpn60(3);Pas_fusA(2);Pas_gltA(2);Pas_pyrG(7);Pas_recA(9);Pas_rplB(1);Pas_rpoB(5) | PERFECT | 100 | none |
| Achromobacter aegrifaciens (GCF_902859965.1) | achromobacter | 468 | nusA(116);rpoB(15);eno(41);gltB(31);lepA(31);nuoL(28);nrdA(30) | PERFECT | 100 | none |
| Aeromonas allosaccharophila (GCF_016026615.1) | aeromonas | - | gyrB(1101?);groL(~740);gltA(~1160);metG(~730);ppsA(~1374);recA(~567) | BAD | 60 | none |
| Avibacterium paragallinarum (GCF_011765605.1) | aparagallinarum | 8 | pmi(3);infB(4);mdh(4);adk(1);deoD(4);recA(4);zwf(6) | PERFECT | 100 | none |
| Anaplasma phagocytophilum str. Webster (GCF_000964685.1) | aphagocytophilum | 64 | pheS(42);glyA(32);fumC(28);mdh(18);sucA(40);dnaN(28);atpA(26) | PERFECT | 100 | none |
| Arcobacter acticola (GCF_013177675.1) | - | - |  | NONE | 0 | none |
| Bartonella bacilliformis KC583 (GCF_000015445.1) | bbacilliformis | 1 | ftsZ(1);flaA(1);ribC(1);rnpB(1);rpoB(1);bvrR(1);groEL(1) | PERFECT | 100 | none |
| Burkholderia aenigmatica (GCF_048627025.1) | bcc | 2120 | atpD(180);gltB(210);gyrB(1351);recA(778);lepA(887);phaC(310);trpB(851) | PERFECT | 100 | none |
| Bacillus cereus ATCC 14579 (GCF_006094295.1) | bcereus | 4 | glp(13);gmk(8);ilv(8);pta(11);pur(11);pyc(12);tpi(7) | PERFECT | 100 | none |
| Bacteroides fragilis NCTC 9343 (GCF_000025985.1) | bfragilis | 26 | dnaJ(4);fusA(3);groL(5);prfA(2);recA(2);rpoB(15);rprX(13) | PERFECT | 100 | none |
| Bartonella henselae (GCF_019930925.1) | bhenselae | 1 | 16S(1,1);batR(1);ftsZ(1);gltA(1);groEL(1);nlpD(1);ribC(1);rpoB(1) | MULTICOPY | 100 | none |
| Bacillus licheniformis (GCF_034478925.1) | blicheniformis_14 | 1 | adk(1);ccpA(1);recF(1);rpoB(1);spo0A(1);sucC(1) | PERFECT | 100 | TIE: blicheniformis_14 (ST1), bsubtilis (ST29) |
| Bordetella pertussis (GCF_004008975.1) | bordetella_3 | 2 | adk(1);fumC(1);glyA(1);tyrB(3);icd(1);pepA(1);pgm(1) | PERFECT | 100 | none |
| Borrelia anserina Es (GCF_001936255.1) | borrelia | 668 | clpA(212);clpX(179);nifS(161);pepX(186);pyrG(196);recG(204);rplB(170);uvrA(188) | PERFECT | 100 | none |
| Burkholderia pseudomallei (GCF_030297255.1) | bpseudomallei | 51 | ace(3);gltB(1);gmhD(2);lepA(3);lipA(1);narK(4);ndh(3) | PERFECT | 100 | none |
| Brachyspira aalborgi (GCF_008016755.1) | - | - |  | NONE | 0 | none |
| Brucella abortus 544 (GCF_000369945.1) | brucella | 1 | gap(2);aroA(1);glk(1);dnaK(2);gyrB(1);trpE(3);cobQ(1);int_hyp(1);omp25(1) | PERFECT | 100 | none |
| Bacillus subtilis subsp. subtilis str. 168 (GCF_000009045.1) | bsubtilis | 1 | glpF(1);ilvD(1);pta(1);purH(1);pycA(1);rpoD(1);tpiA(1) | PERFECT | 100 | none |
| Candidatus Bartonella washoeensis Sb944nv (GCF_000278135.1) | bwashoensis | - | 16S(1);ftsZ(10);gltA(10);groEL(15);ribC(~15);rpoB(14) | PARTIAL | 85 | none |
| Campylobacter jejuni subsp. jejuni NCTC 11168 = ATCC 700819 (GCF_000009085.1) | campylobacter | 43 | aspA(2);glnA(1);gltA(5);glyA(3);pgm(4);tkt(1);uncA(5) | PERFECT | 100 | none |
| Campylobacter helveticus (GCF_002080395.1) | campylobacter_nonjejuni | 1 | Che_aspA(1);Che_atpA(1);Che_glnA(1);Che_gltA(1);Che_glyA(1);Che_pgm(1);Che_tkt(1) | PERFECT | 100 | none |
| Campylobacter insulaenigrae NCTC 12927 (GCF_000816185.1) | campylobacter_nonjejuni_2 | 1 | Cin_aspA(1);Cin_atpA(1);Cin_glnA(1);Cin_glyA(1);Cin_pgi(1);Cin_pgm(1);Cin_tkt(1) | PERFECT | 100 | none |
| Campylobacter lari subsp. concheus (GCF_008245025.1) | campylobacter_nonjejuni_3 | - | Cla_adk(26);Cla_atpA(26);Cla_glnA(5);Cla_glyA(~10);Cla_pgi(25);Cla_pgm(7);Cla_tkt(16) | PARTIAL | 86 | none |
| Campylobacter upsaliensis RM3940 (GCF_013372245.1) | campylobacter_nonjejuni_4 | 20 | Cup_adk(6);Cup_aspA(15);Cup_atpA(1);Cup_glnA(13);Cup_glyA(11);Cup_pgi(1);Cup_tkt(11) | PERFECT | 100 | none |
| Campylobacter concisus (GCF_001298465.1) | campylobacter_nonjejuni_5 | 77 | Cco_aspA(68);Cco_atpA(49);Cco_glnA(4);Cco_gltA(4);Cco_glyA(4);Cco_ilvD(4);Cco_pgm(4) | PERFECT | 100 | none |
| Campylobacter hyointestinalis subsp. lawsonii (GCF_013372165.1) | campylobacter_nonjejuni_6 | 8 | Chy_aspA(3);Chy_atpA(4);Chy_glnA(6);Chy_gltA(5);Chy_glyA(5);Chy_pgm(6);Chy_tkt(8) | PERFECT | 100 | none |
| Campylobacter lanienae NCTC 13004 (GCF_002139935.1) | campylobacter_nonjejuni_7 | 2 | Cln_aspA(2);Cln_atpA(2);Cln_glnA(2);Cln_gltA(2);Cln_glyA(2);Cln_pgm(2);Cln_tkt(2) | PERFECT | 100 | none |
| Campylobacter sputorum subsp. sputorum (GCF_008245005.1) | campylobacter_nonjejuni_8 | 1 | Csp_aspA(1);Csp_atpA(1);Csp_glnA(1);Csp_gltA(1);Csp_glyA(1);Csp_pgm(1);Csp_tkt(1) | PERFECT | 100 | none |
| Campylobacter fetus (GCF_011600945.2) | campylobacter_nonjejuni_9 | 6 | Cfe_aspA(1);Cfe_glnA(2);Cfe_gltA(2);Cfe_glyA(2);Cfe_pgm(1);Cfe_tkt(2);Cfe_uncA(4) | PERFECT | 100 | none |
| Clostridium botulinum A str. ATCC 3502 (GCF_000063585.1) | cbotulinum | 9 | aroE(13);mdh(6);aceK(9);oppB(10);rpoB(9);recA(8);hsp(9) | PERFECT | 100 | none |
| Clostridioides difficile (GCF_018885085.1) | cdifficile | 8 | adk(1);atpA(1);dxr(2);glyA(6);recA(1);sodA(5);tpi(1) | PERFECT | 100 | none |
| Corynebacterium diphtheriae (GCF_001457455.1) | cdiphtheriae | 26 | atpA(8);dnaE(2);dnaK(16);fusA(1);leuA(3);odhA(3);rpoB(12) | PERFECT | 100 | TIE: cdiphtheriae (ST26), diphtheria_3 (ST26) |
| Citrobacter amalonaticus (GCF_020099335.1) | cfreundii | 710 | aspC(137);clpX(152);fadD(215);mdh(212);arcA(75);dnaG(184);lysP(186) | PERFECT | 100 | none |
| Candidatus Chlamydia corallus (GCF_002817655.1) | chlamydiales | 265 | gatA(79);oppA(73);hflX(84);gidA(86);enoA(90);hemN(70,70);fumC(72) | MULTICOPY | 100 | none |
| Carnobacterium maltaromaticum (GCF_949790605.1) | cmaltaromaticum | - | dapE(12);ddlA(4);glpQ(7);ilvE(4);leuS(3);pyc(10);pyrE(3) | NOVEL | 90 | none |
| Clostridium perfringens (GCF_016027375.1) | cperfringens | - | colA(2);groEL(3);sodA(1);plc(10);gyrB(3);sigK(2);pgk(1);nadA(114) | NOVEL | 90 | none |
| Cronobacter condimenti 1330 (GCF_001277255.1) | cronobacter | 98 | atpD(24);fusA(86);glnS(96);gltB(28);gyrB(63);infB(42);pps(147) | PERFECT | 100 | none |
| Clostridium septicum (GCF_003606265.1) | csepticum | 22 | ddl(1);dnaK(3);glpK(1);groEL(1);gyrA(1);recA(1);tpi(1) | PERFECT | 100 | none |
| Dichelobacter nodosus VCS1703A (GCF_000015345.1) | dnodosus | 19 | dcd(1);dtdA(1);folK(1);recR(1);rlmH(1);rplI(1);tsaE(1) | PERFECT | 100 | none |
| Enterobacter adelaidei (GCF_041937165.1) | ecloacae | 928 | dnaA(280);fusA(178);gyrB(299);leuS(335);pyrG(274);rplB(106);rpoB(156) | PERFECT | 100 | none |
| Escherichia coli O157:H7 str. Sakai (GCF_000008865.2) | ecoli_achtman_4 | 11 | adk(12);fumC(12);gyrB(8);icd(12);mdh(15);purA(2);recA(2) | PERFECT | 100 | none |
| Edwardsiella anguillarum ET080813 (GCF_000264765.2) | edwardsiella | - | adk(8);atpD(6);dnaJ(11);gapA(13);glnA(10);hsp60(8);phoR(13);pyrG(14);rpoA(3);tuf(8) | NOVEL | 90 | none |
| Enterococcus faecalis EnGen0336 (GCF_000393015.1) | efaecalis | 68 | gdh(6);gyd(2);pstS(11);gki(5);aroE(10);xpt(1);yqiL(22) | PERFECT | 100 | none |
| Enterococcus faecium (GCF_009734005.1) | efaecium | 78 | atpA(15);ddl(1);gdh(1);purK(1);gyd(1);pstS(1);adk(1) | PERFECT | 100 | none |
| Flavobacterium psychrophilum FPG3 (GCF_000754405.1) | fpsychrophilum | 13 | atpA(4);dnaK(6);fumC(5);gyrB(7);murG(6);trpB(4);tuf(8) | PERFECT | 100 | none |
| Gallibacterium anatis DSM 16844 = F 149 (GCF_000772265.1) | gallibacterium | - | adk(14);atpD(21);fumC(~22);gyrB(7);infB(32);mdh(9?);recN(21);thdF(6) | PARTIAL | 81 | none |
| Geotrichum candidum (GCA_013365045.1) | geotrichum | - | NUP116(8);URA1(6);URA3(4);SAPT4(2?);PLB3(5) | PARTIAL | 81 | none |
| Candidatus Halobonum tyrrellensis G22 (GCF_000495475.1) | - | - |  | NONE | 0 | none |
| Helicobacter cinaedi PAGU611 (GCF_000284635.1) | hcinaedi | 8 | 23S_rRNA(3,3);ppa(4);aspA(4);aroE(3);atpA(2);tkt(3);cdtB(2) | MULTICOPY | 100 | none |
| Helicobacter pylori (GCF_025998455.1) | helicobacter | - | atpA(2663);efp(2487);mutY(2684);ppa(1965);trpC(1536);ureI(2754);yphC(2775) | NOVEL | 90 | none |
| Haemophilus influenzae (GCF_020736045.1) | hinfluenzae | 3 | adk(1);atpG(1);frdB(1);fucK(1);mdh(1);pgi(1);recA(5) | PERFECT | 100 | none |
| Glaesserella parasuis (GCF_017352235.1) | hparasuis | 428 | atpD(7);infB(67);mdh(34);rpoB(1);6pgd(43);g3pd(3);frdB(39) | PERFECT | 100 | none |
| Helicobacter suis (GCF_013374215.1) | hsuis | 141 | atpA(14);efp(2);mutY(77);ppa(32);trpC(1);ureAB(1);yphC(1) | PERFECT | 100 | none |
| Klebsiella aerogenes (GCF_019048125.1) | kaerogenes | 134 | dnaA(31);fusA(3);gyrB(1);leuS(4);pryG(3);rplB(1);rpoB(2) | PERFECT | 100 | none |
| Kingella kingae (GCF_900475905.1) | kingella | 1 | abcZ(1);adk(1);aroE(1);cpn60(1);gdh(1);recA(1) | PERFECT | 100 | none |
| Klebsiella pneumoniae subsp. pneumoniae HS11286 (GCF_000240185.1) | ecoli_achtman_4 | 14464 | adk(1769);fumC(1664);gyrB(193);icd(1804);mdh(986);purA(745);recA(866) | PERFECT | 100 | TIE: ecoli_achtman_4 (ST14464), klebsiella (ST11) |
| Klebsiella oxytoca (GCF_900636985.1) | koxytoca | 199 | gapA(2);infB(2);mdh(2);pgi(3);phoE(19);rpoB(2);tonB(2) | PERFECT | 100 | none |
| Leptospira abararensis (GCF_016918735.1) | - | - |  | NONE | 0 | none |
| Lactococcus garvieae (GCF_016026695.1) | lgarvieae | 1 | als(1);atpA(1);tuf(1);gapC(1);gyrB(1);rpoC(1);galP(1) | PERFECT | 100 | none |
| Candidatus Liberibacter africanus PTSAPSY (GCF_001021085.1) | - | - |  | NONE | 0 | none |
| Listeria monocytogenes EGD-e (GCF_000196035.1) | listeria_2 | 35 | abcZ(6);bglA(5);cat(6);dapE(20);dat(1);ldh(4);lhkA(1) | PERFECT | 100 | none |
| Lactococcus phage 936 (GCF_002592905.1) | llactis_phage | 269 | terL(4);mcp(3);mtp(121);tmp(164);lys(61) | PERFECT | 100 | none |
| Ligilactobacillus salivarius (GCF_035231985.1) | lsalivarius | - | pstB(~12);rpsB(7);nrdB(5?);rpoA(6);parB(~17) | PARTIAL | 70 | none |
| Mycobacteroides abscessus ATCC 19977 (GCF_000069185.1) | mabscessus | 5 | argH(3);cya(1);gnd(4);murC(3);pta(1);purH(2);rpoB(1) | PERFECT | 100 | TIE: mabscessus (ST5), mycobacteria_2 (ST5) |
| Mycoplasmopsis agalactiae PG2 (GCF_000063605.1) | magalactiae | 1 | dnaA(1);gltX(1);gyrB(1);metS(1);tufA(1) | PERFECT | 100 | none |
| Mycoplasma amphoriforme A39 (GCF_000723365.1) | mamphoriforme | 1 | atpG(1);gyrB(1);rpoB(1);uvrA(1) | PERFECT | 100 | none |
| Mycoplasma anserisalpingitidis (GCF_007859615.1) | manserisalpingitidis | 1 | atpG(1);fusA(1);pgiB(1);plsY(1);uvrA(1) | PERFECT | 100 | none |
| Mycoplasmopsis bovis PG45 (GCF_000183385.1) | mbovis | 17 | adh1(3);gltX(2);gpsA(4);gyrB(2);pta2(1);tdk(3);tkt(2) | PERFECT | 100 | TIE: mbovis (ST17), mbovis_2 (ST12) |
| Macrococcoides canis (GCF_002119805.1) | mcanis | 1 | ack(1);cpn60(1);fdh(1);pta(1);purA(1);sar(1);tuf(1) | PERFECT | 100 | none |
| Macrococcoides caseolyticum (GCF_016028795.1) | mcaseolyticus | 4 | ack(3);cpn60(3);fdh(4);pta(3);purA(4);sar(3);tuf(3) | PERFECT | 100 | none |
| Moraxella catarrhalis (GCF_900476075.1) | mcatarrhalis_achtman_6 | 54 | abcZ(8);adk(24);efp(3);fumC(7);glyBeta(30);mutY(3);ppa(23);trpE(2) | PERFECT | 100 | none |
| Mesomycoplasma flocculare ATCC 27399 (GCF_000815065.1) | mflocculare | 1 | adk(1);rpoB(1);tpiA(1) | PERFECT | 100 | none |
| Mycoplasmoides gallisepticum (GCF_900476085.1) | mgallisepticum | 23 | atpG(2);dppC(25);DUF3196(2);lgT(26);mraW(1);plsC(10);ugpA(1) | PERFECT | 100 | TIE: mgallisepticum (ST23), mgallisepticum_2 (ST1) |
| Mycoplasmoides genitalium (GCF_040556925.1) | mgenitalium | - | MLST_adk(1);MLST_atpA(1);MLST_gmk(1);MLST_gyrB(1);MLST_pgm(1);MLST_ppa(1) | NOVEL | 90 | none |
| Mannheimia haemolytica (GCF_002285575.1) | mhaemolytica | 1 | adk(1);aroE(2);deoD(1);gapDH(2);gnd(1);mdh(2);zwf(1) | PERFECT | 100 | none |
| Metamycoplasma hominis ATCC 27545 (GCF_000767725.1) | mhominis | - | uvrA(19);gyrB(16);ftsY(18);tuf(7);gap(25) | NOVEL | 90 | none |
| Mesomycoplasma hyopneumoniae J (GCF_000008205.1) | mhyopneumoniae | 28 | adk(5);rpoB(16);tpiA(16) | PERFECT | 100 | none |
| Mesomycoplasma hyorhinis (GCF_900476065.1) | mhyorhinis | 16 | dnaA(1);rpoB(3);gyrB(1);gltX(1);adk(1);gmk(3) | PERFECT | 100 | none |
| Metamycoplasma hyosynoviae (GCF_024297005.1) | mhyosynoviae | 45 | dnaA(2);ftsY(15);fusA(9);gyrB(1);recA(9);rpoB(14);uvrA(15) | PERFECT | 100 | none |
| Malacoplasma iowae (GCF_900660615.1) | miowae | 10 | dppC(1);ulaA(7);valS(5);rpoC(1);leuS(1);kdpA(1) | PERFECT | 100 | none |
| Melissococcus plutonius (GCF_003966875.1) | mplutonius | 12 | argE(4);galK(4);gbpB(3);purR(5) | PERFECT | 100 | none |
| Mycoplasmoides pneumoniae (GCF_900660465.1) | mpneumoniae | 2 | ppa(2);pgm(3);gyrB(2);gmk(2);glyA(2);atpA(4);arcC(1);adk(1) | PERFECT | 100 | none |
| Mammaliicoccus sciuri (GCF_900474615.1) | msciuri | 30 | ack(9);aroE(10);ftsZ(8);glpK(10);gmk(6);pta1(5);tpiA(10) | PERFECT | 100 | none |
| Mycoplasmopsis synoviae ATCC 25204 (GCF_000969765.1) | msynoviae | 44 | adk(2);atpG(3);efp(2);gmk(3);nagC(3);ppa(2);recA(3) | PERFECT | 100 | none |
| Candidatus Mycobacterium methanotrophicum (GCF_023515995.1) | - | - |  | NONE | 0 | none |
| Neisseria meningitidis (GCF_022869645.1) | neisseria | 4 | abcZ(1);adk(3);aroE(3);fumC(1);gdh(4);pdhC(2);pgm(3) | PERFECT | 100 | none |
| Streptococcus oralis ATCC 35037 (GCF_900637025.1) | oralstrep | - | aroE(63);ddl(~19);gdh(~8);gki(~13);hexB(~42);recP(10);xpt(17) | PARTIAL | 74 | none |
| Ornithobacterium rhinotracheale DSM 15997 (GCF_000265465.1) | orhinotracheale | 1 | adk(1);aroE(1);fumC(1);gdhA(1);mdh(1);pgi(1);pmi(1) | PERFECT | 100 | none |
| Orientia tsutsugamushi (GCF_900327255.1) | otsutsugamushi | 1 | gpsA(1);mdh(1);nrdB(1);nuoF(1);ppdK(1);sucB(1);sucD(1) | PERFECT | 100 | none |
| Cutibacterium acnes subsp. acnes (GCF_006739385.1) | pacnes_3 | - | aroE(1);atpD(1);gmk(1);guaA(3);lepA(1);sodA(1);tly(1);CAMP2(~1) | PARTIAL | 86 | none |
| Pseudomonas aeruginosa PAO1 (GCF_000006765.1) | paeruginosa | 549 | acsA(7);aroE(5);guaA(12);mutL(3);nuoD(4);ppsA(1);trpE(7) | PERFECT | 100 | none |
| Photobacterium damselae subsp. damselae (GCF_038086725.1) | vibrio | - | gyrB(~247);pyrH(209);recA(~238);atpA(~174) | BAD | 69 | none |
| Pseudomonas fluorescens (GCF_900215245.1) | pfluorescens | 128 | glnS(22);gyrB(22);ileS(102);nuoD(22);recA(22);rpoB(96);rpoD(22) | PERFECT | 100 | none |
| Porphyromonas gingivalis ATCC 33277 (GCF_000010505.1) | pgingivalis | 96 | ftsQ(5);gpdxJ(9);hagB(1,1);mcmA(1);pepO(1);pga(5);recA(5) | MULTICOPY | 100 | none |
| Paenibacillus larvae subsp. larvae (GCF_002951935.1) | plarvae | 8 | glpF(1);sigF(2);glpT(2);Natrans(1);rpoB(2);ftsA(1);clpC(1) | PERFECT | 100 | none |
| Pasteurella multocida (GCF_002073255.2) | pmultocida | 124 | mh_adk(10);mh_aroA(40);mh_deoD(3);mh_gdhA(29);mh_g6pd(29);mh_mdh(16);mh_pgi(33) | PERFECT | 100 | TIE: pmultocida (ST124), pmultocida_2 (ST8) |
| Pediococcus pentosaceus ATCC 25745 (GCF_000014505.1) | ppentosaceus | 1 | gyrB(1);pyc(1);pgm(1);leuS(1);glnA(1);dalR(1);pgI(1) | PERFECT | 100 | none |
| Pseudomonas putida NBRC 14164 (GCF_000412675.1) | pputida | 2 | argS(3);gyrB(15);ileS(29);nuoC(5);ppsA(17);recA(20);rpoB(10);rpoD(21) | PERFECT | 100 | none |
| Proteus alimentorum (GCF_002607735.1) | proteus | 3 | atpD(4);dnaJ(6);mdh(3);pyrC(4);recA(3);rpoD(3) | PERFECT | 100 | none |
| Candidatus Providencia siddallii (GCF_964026685.1) | - | - |  | NONE | 0 | none |
| Piscirickettsia salmonis (GCF_009708955.1) | psalmonis | 2 | dnaK(2);efp(2);fumC(2);glyA(2);murG(2);rpoD(1);trpB(2) | PERFECT | 100 | none |
| Riemerella anatipestifer ATCC 11845 = DSM 15868 (GCF_000183155.1) | ranatipestifer | 15 | dnaB(2);groEL(1);gyrA(1);mdh(1);gluD(1);gpi(3);rpoB(3) | PERFECT | 100 | none |
| Rhodococcus (subgen. Prescottella) agglutinans (GCF_004011865.1) | - | - |  | NONE | 0 | none |
| Streptococcus agalactiae (GCF_949788565.1) | sagalactiae | 728 | adhP(126);pheS(1);atr(2);glnA(2);sdhA(9);glcK(2);tkt(2) | PERFECT | 100 | none |
| Salmonella enterica subsp. enterica serovar Typhimurium str. LT2 (GCF_000006945.2) | salmonella | 19 | aroC(10);dnaN(7);hemD(12);hisD(9);purE(5);sucA(9);thrA(2) | PERFECT | 100 | none |
| Staphylococcus aureus subsp. aureus NCTC 8325 (GCF_000013425.1) | saureus | 8 | arcC(3);aroE(3);glpF(1);gmk(1);pta(4);tpi(4);yqiL(3) | PERFECT | 100 | none |
| Streptococcus equinus (GCF_049393805.1) | sbsec | - | ddl(~11);gki(~45);glnA(~10);mutS(~59);mutS2(28?);pheS(43);proS(~58);pyrE(~71);thrS(~40);tpi(~28) | BAD | 63 | none |
| Staphylococcus chromogenes (GCF_007814525.1) | schromogenes | 95 | arcC(33);hutU(20);fumC(8);dnaJ(7);glpF(28);menF(7);pta(7) | PERFECT | 100 | none |
| Streptococcus dysgalactiae (GCF_016128095.1) | sdysgalactiae | 61 | gki(3);gtr(3);murI(4);mutS(1);recP(4);xpt(16);atoB(2) | PERFECT | 100 | none |
| Staphylococcus epidermidis (GCF_006094375.1) | sepidermidis | 5 | arcC(1);aroE(1);gtr(1);mutS(2);pyrR(2);tpiA(1);yqiL(1) | PERFECT | 100 | none |
| Serratia aquatilis (GCF_044865145.1) | - | - |  | NONE | 0 | none |
| Streptococcus gallolyticus (GCF_013267695.1) | sbsec | 34 | ddl(9);gki(8);glnA(7);mutS(9);mutS2(19);pheS(9);proS(15);pyrE(23);thrS(21);tpi(8) | PERFECT | 100 | TIE: sbsec (ST34), sgallolyticus (ST117) |
| Staphylococcus haemolyticus (GCF_006094395.1) | shaemolyticus | 26 | arcC(1);SH_1200(5);hemH(6);leuB(1);SH1431(5);cfxE(1);Ribose_ABC(1) | PERFECT | 100 | none |
| Shewanella abyssi (GCF_023284025.1) | - | - |  | NONE | 0 | none |
| Staphylococcus hominis (GCF_003812505.1) | shominis | 96 | arcC(28);glpK(8);gtr(1);pta(3);tpiA(8);tuf(4) | PERFECT | 100 | none |
| Streptococcus iniae (GCF_000831485.1) | siniae | - | dnaN(1);mutL(1);mutM(1);mutS(3);mutX(2?);recD2(1);rnhC(1);yfhQ(1) | PARTIAL | 84 | none |
| Sinorhizobium alkalisoli (GCF_008932245.1) | - | - |  | NONE | 0 | none |
| Stenotrophomonas acidaminiphila (GCF_014109845.1) | smaltophilia | - | atpD(~46);gapA(~46);guaA(~55);mutM(~40);nuoD(48?);ppsA(~50);recA(~41) | BAD | 60 | none |
| Streptococcus mitis (GCF_018603625.2) | smitis | - | accA(94?);gki(37);hom(~16);oppC(67);patB(130);rlmN(~63);tsf(142) | PARTIAL | 75 | none |
| Streptococcus pneumoniae (GCF_001457635.1) | spneumoniae | 615 | aroE(10);gdh(31);gki(4);recP(1);spi(6);xpt(4);ddl(94) | PERFECT | 100 | none |
| Staphylococcus pseudintermedius (GCF_034042775.1) | spseudintermedius | 2340 | ack(5);cpn60(2);fdh(4);pta(1);purA(11);sar(1);tuf(1) | PERFECT | 100 | none |
| Streptococcus pyogenes (GCF_900475035.1) | spyogenes | 103 | gki(2);gtr(2);murI(2);mutS(3);recP(37);xpt(3);yqiL(2) | PERFECT | 100 | none |
| Streptococcus suis BM407 (GCF_000026745.1) | ssuis | 1 | aroA(1);cpn60(1);dpr(1);gki(1);mutS(1);recA(1);thrA(1) | PERFECT | 100 | none |
| Staphylococcus lugdunensis (GCF_001558775.1) | staphlugdunensis | 3 | aroE(4);dat(3);ddl(4);gmk(2);ldh(3);recA(4);yqiL(6) | PERFECT | 100 | none |
| Streptococcus thermophilus (GCF_903886475.1) | streptothermophilus | 59 | ddlA(2);glcK(1);proA(1);ptsI(2);serB(4);tkt(1) | PERFECT | 100 | none |
| Candidatus Streptomyces philanthi (GCF_059553635.1) | - | - |  | NONE | 0 | none |
| Streptococcus uberis (GCF_900475595.1) | suberis | 1210 | arcC(8);ddl(2);gki(3);recP(16);tdk(3);tpi(1);yqiL(3) | PERFECT | 100 | none |
| Streptococcus equi subsp. zooepidemicus (GCF_015689395.1) | szooepidemicus | 218 | arcC(8);nrdE(3);proS(43);spi(6);tdk(30);tpi(3);yqiL(22) | PERFECT | 100 | none |
| Taylorella asinigenitalis MCE3 (GCF_000226625.1) | taylorella | 21 | gltA(3);gyrB(7);fh(12);shmt(6);tyrB(10);adk(6);txn(7) | PERFECT | 100 | none |
| Tenacibaculum adriaticum (GCF_008124875.1) | tenacibaculum | 66 | atpA(1012);dnaK(1015);glyA(1015);gyrB(1014);infB(1013);rlmN(1015);tgt(1012) | PERFECT | 100 | none |
| Treponema pallidum subsp. pallidum str. Nichols (GCF_000410535.2) | tpallidum | 20 | TP0136(10);TP0548(14);TP0705(10) | PERFECT | 100 | none |
| Trueperella pyogenes (GCF_001281085.1) | tpyogenes | 49 | adk(6);gyrB(5);leuA(2);metG(22);recA(7);tpi(29);tuf(1) | PERFECT | 100 | none |
| Trichomonas vaginalis G3 (GCF_026262505.1) | tvaginalis | 1 | TRYP(1);GLUT(1);FT2A(1);ALTS(1);DMRP(1);SHMT(1);M6PI(1) | PERFECT | 100 | none |
| Ureaplasma canigenitalium ATCC 51252 (GCF_000712165.1) | - | - |  | NONE | 0 | none |
| Vibrio cholerae (GCF_008369605.1) | vcholerae | - | adk(18);gyrB(41);mdh(14);metE(~156);pntA(71);purM(119);pyrC(35) | PARTIAL | 86 | none |
| Vibrio cholerae IEC224 (GCF_000250855.1) | vcholerae | 69 | adk(7);gyrB(11);mdh(4);metE(37);pntA(12);purM(1);pyrC(20) | PERFECT | 100 | none |
| Vibrio aerogenes (GCF_024346755.1) | - | - |  | NONE | 0 | none |
| Vibrio parahaemolyticus RIMD 2210633 (GCF_000196095.1) | vibrio | 152 | gyrB(130);pyrH(101);recA(62);atpA(19) | PERFECT | 100 | TIE: vibrio (ST152), vparahaemolyticus (ST3) |
| Vibrio tapetis subsp. quintayensis (GCF_030409945.1) | - | - |  | NONE | 0 | none |
| Vibrio vulnificus NBRC 15645 = ATCC 27562 (GCF_002224265.1) | vibrio | 126 | gyrB(104);pyrH(80);recA(98);atpA(77) | PERFECT | 100 | TIE: vibrio (ST126), vvulnificus (ST3) |
| Candidatus Wolbachia massiliensis (GCF_014771645.1) | - | - |  | NONE | 0 | none |
| Xylella fastidiosa (GCF_028891345.1) | xfastidiosa | 2 | leuA(1);petC(1);malF(4);cysG(1);holC(1);nuoL(1);gltT(1) | PERFECT | 100 | none |
| Yersinia aldovae 670-83 (GCF_000834395.1) | ypseudotuberculosis_achtman_3 | 217 | adk(56);argA(59);aroA(64);glnA(61);thrA(69);tmk(69);trpE(67) | PERFECT | 100 | none |
| Yersinia pseudotuberculosis (GCF_900637475.1) | yersinia | 90 | aarF(39);dfp(43);galR(51);glnS(56);hemA(44);rfaE(42);speA(41) | PERFECT | 100 | TIE: yersinia (ST90), ypseudotuberculosis_achtman_3 (ST9) |
| Yersinia ruckeri (GCF_017498685.1) | yersinia | 44 | aarF(13);dfp(10);galR(14);glnS(13);hemA(15);rfaE(14);speA(14) | PERFECT | 100 | TIE: yersinia (ST44), ypseudotuberculosis_achtman_3 (ST276), yruckeri (ST33) |
| Streptococcus pyogenes (Group A Strep) SF370 (GCF_000006785.2) | spyogenes | 28 | gki(4);gtr(3);murI(4);mutS(4);recP(4);xpt(2);yqiL(4) | PERFECT | 100 | none |
| Neisseria gonorrhoeae FA 1090 (GCF_000006845.1) | neisseria | 1899 | abcZ(109);adk(39);aroE(67);fumC(190);gdh(147);pdhC(71);pgm(65) | PERFECT | 100 | none |
| Shigella sonnei Ss046 (GCF_000092525.1) | ecoli_achtman_4 | 152 | adk(11);fumC(63);gyrB(7);icd(1);mdh(14);purA(7);recA(7) | PERFECT | 100 | none |
| Shigella flexneri 2a 301 (GCF_000006925.2) | ecoli_achtman_4 | 245 | adk(6);fumC(61);gyrB(6);icd(11);mdh(13);purA(3);recA(50) | PERFECT | 100 | none |
| Mycobacterium tuberculosis H37Rv (GCF_000195955.2) | mycobacteria_2 | 215 | S14Z(17);L35(15);S19(20);L19(19);S12(20);S8(18);L16(22);S7(19) | PERFECT | 100 | none |
| Aliarcobacter butzleri 6V (GCF_004283115.1) | arcobacter | 537 | aspA(236);atpA(161);glnA(1);gltA(183);glyA(521);pgm(296);tkt(207) | PERFECT | 100 | none |
| Brachyspira hyodysenteriae ATCC 27164 (GCF_001676785.2) | brachyspira | 5 | Bra_adh(1);Bra_alp(4);Bra_est(4);Bra_gdh(5);Bra_glp(7);Bra_pgm(2);Bra_thi(3) | PERFECT | 100 | TIE: brachyspira (ST5), brachyspira_2 (ST56) |
| Brachyspira hyodysenteriae BH718 (GCF_002850235.1) | brachyspira_2 | 83 | Bhy_adh(2);Bhy_alp(11);Bhy_est(3);Bhy_gdh(5);Bhy_glpK(12);Bhy_pgm(2);Bhy_thi(6) | PERFECT | 100 | none |
| Brachyspira intermedia PWS/A (GCF_000223215.1) | brachyspira_3 | - | Bin_adh(10);Bin_alp(15);Bin_est(26);Bin_gdh(17);Bin_glpK(25);Bin_pgm(26);Bin_thi(25) | NOVEL | 90 | none |
| Brachyspira pilosicoli 95/1000 (GCF_000143725.1) | brachyspira_4 | 138 | Bpi_adh(5);Bpi_alp(71);Bpi_est(39);Bpi_gdh(34);Bpi_glpK(64);Bpi_pgm(93);Bpi_thi(72) | PERFECT | 100 | none |
| Brachyspira hampsonii 30446 (GCF_000316195.1) | brachyspira_5 | 7 | Bha_adh(2);Bha_est(2);Bha_gdh(2);Bha_glpK(3);Bha_pgm(3);Bha_thi(1) | PERFECT | 100 | none |
| Halorubrum lacusprofundi ATCC 49239 (GCF_000022205.1) | halobacteria | - | atpB(4);EF-2(4);radA(4);rpoB'(3);secY(4) | NOVEL | 90 | none |
| Leptospira interrogans serovar Copenhageni FDAARGOS_203 (GCF_002073495.2) | leptospira | 17 | glmU_1(1);pntA_1(1);sucA_1(2);tpiA_1(2);pfkB_1(10);mreA_1(4);caiB_1(8) | PERFECT | 100 | TIE: leptospira (ST17), leptospira_2 (ST47), leptospira_3 (ST2) |
| Leptospira interrogans CUDO5 (GCF_002370085.3) | leptospira | 26 | glmU_1(1);pntA_1(18);sucA_1(2);tpiA_1(2);pfkB_1(4);mreA_1(6);caiB_1(6) | PERFECT | 100 | TIE: leptospira (ST26), leptospira_3 (ST188) |
| Candidatus Liberibacter solanacearum CLso-ZC1 (GCF_000183665.1) | liberibacter | 10 | adk(5);atpA(6);fbpA(5);ftsZ(8);glyA(5);groEL(5);gyrB(7) | PERFECT | 100 | none |
| Providencia stuartii 41 (GCF_035747985.1) | providencia | 233 | fusA(7);gyrB(7);ileS(12);lepA(20);leuS(12) | PERFECT | 100 | none |
| Rhodococcus (Prescottella) equi WY (GCF_007197835.1) | rhodococcus | 36 | gapdh(3);tpi(3);mdh(3);icl(8);rpoB(15);recA(2);adk(2) | PERFECT | 100 | none |
| Serratia marcescens ELP1.10 (GCF_030291735.1) | serratia | 1305 | adk(52);fumC(163);gyrB(343);icd(62);mdh(123);recA(61) | PERFECT | 100 | none |
| Shewanella algae MARS 14 (GCF_000947195.1) | shewanella | 26 | 16S_rRNA(6);adk(1);atpB(1);guaA(24);gyrB(23);mdh(12);recA(22);rpoS(21) | PERFECT | 100 | none |
| Sinorhizobium (Ensifer) meliloti MABNR56 (GCF_037023865.1) | sinorhizobium | 9 | asd(1);edd(6);gap(4);glnD(6);gnd(3);nuoE1(3);ordL2(5);recA(4);sucA(5);zwf(1) | PERFECT | 100 | none |
| Streptomyces griseus NRRL B-2165 (GCF_001723115.1) | streptomyces | 12 | 16S(6);atpD(6);gyrB(8);recA(8);rpoB(8);trpB(8) | PERFECT | 100 | none |
| Ureaplasma parvum serovar 3 ATCC 27815 (GCF_000019345.1) | ureaplasma | 2 | ftsH(2);rpL22(1);thrS(1);valS(1) | PERFECT | 100 | none |
| Vibrio tapetis subsp. tapetis (GCF_900233005.1) | vtapetis | - | atpA(1);fstZ(1);gapA(1);hsp60(1);pyrH(1);rctB(1?);recA(1);rpoA(1);rpoD(1?);topA(1) | PARTIAL | 81 | none |
| Wolbachia endosymbiont of Drosophila melanogaster wMelPlus (GCF_947533255.1) | wolbachia | 1 | gatB(1);coxA(1);hcpA(1);ftsZ(1);fbpA(1) | PERFECT | 100 | none |
| Aeromonas hydrophila subsp. hydrophila ATCC 7966 (GCF_000014805.1) | aeromonas | 1 | gyrB(1);groL(1);gltA(1);metG(1);ppsA(1);recA(1) | PERFECT | 100 | none |
| Photobacterium damselae subsp. piscicida AS-16-0555-7 (GCF_014775695.1) | pdamselae | 46 | glpF(19);gyrB(20);metG(6);pntA(16);pyrC(20);toxR(26) | PERFECT | 100 | none |
| Streptococcus canis NCTC12191 (GCF_900636575.1) | scanis | 9 | gki(3);gtr(5);murI(3);mutS(3);recP(1);xpt(2);yqiZ(3) | PERFECT | 100 | none |
| Stenotrophomonas maltophilia ISMMS3 (GCF_001274595.1) | smaltophilia | 280 | atpD(26);gapA(116);guaA(154);mutM(103);nuoD(3);ppsA(159);recA(110) | PERFECT | 100 | none |
