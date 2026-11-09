# Validation, database PubMLST_2026-11

Run 2026-11-10: 168 genomes listed (one public NCBI assembly per scheme + priority organisms).

- Typed: 168 (0 without a genome)
- Called the scheme the genome was picked for: 127/168
- PERFECT (full ST): 119/168
- Same result as upstream mlst on the same database: **156/168**
- Upstream picked another of the tied schemes this run: 12/168 (see Ties)
- Real differences: **0/168**

## Priority organisms

| Genome | Scheme | ST | Status | Alleles |
|---|---|---|---|---|
| Streptococcus pyogenes (Group A Strep) SF370 (GCF_000006785.2) | spyogenes | 28 | PERFECT | gki(4);gtr(3);murI(4);mutS(4);recP(4);xpt(2);yqiL(4) |
| Neisseria gonorrhoeae FA 1090 (GCF_000006845.1) | neisseria | 1899 | PERFECT | abcZ(109);adk(39);aroE(67);fumC(190);gdh(147);pdhC(71);pgm(65) |
| Salmonella enterica Typhimurium LT2 (GCF_000006945.2) | salmonella | 19 | PERFECT | aroC(10);dnaN(7);hemD(12);hisD(9);purE(5);sucA(9);thrA(2) |
| Shigella sonnei Ss046 (GCF_000092525.1) | ecoli_achtman_4 | 152 | PERFECT | adk(11);fumC(63);gyrB(7);icd(1);mdh(14);purA(7);recA(7) |
| Shigella flexneri 2a 301 (GCF_000006925.2) | ecoli_achtman_4 | 245 | PERFECT | adk(6);fumC(61);gyrB(6);icd(11);mdh(13);purA(3);recA(50) |
| Mycobacterium tuberculosis H37Rv (GCF_000195955.2) | mycobacteria_2 | 215 | PERFECT | S14Z(17);L35(15);S19(20);L19(19);S12(20);S8(18);L16(22);S7(19) |

## Real differences from upstream mlst (0)

None.

## Ties (same top score for more than one scheme) (12)

Two or more schemes give these genomes the same top score. Upstream mlst picks one of them at random (its answer can change from run to run); mlst-typing always reports the first by name and prints a warning listing the others.

| Genome | Tied schemes | mlst-typing reports | upstream mlst (this run) | Score |
|---|---|---|---|---|
| Bacillus licheniformis (GCF_034478925.1) | blicheniformis_14 ST1, bsubtilis ST29 | blicheniformis_14 ST1 | bsubtilis ST29 | 100 |
| Corynebacterium diphtheriae (GCF_001457455.1) | cdiphtheriae ST26, diphtheria_3 ST26 | cdiphtheriae ST26 | diphtheria_3 ST26 | 100 |
| Klebsiella pneumoniae subsp. pneumoniae HS11286 (GCF_000240185.1) | ecoli_achtman_4 ST14464, klebsiella ST11 | ecoli_achtman_4 ST14464 | klebsiella ST11 | 100 |
| Mycobacteroides abscessus ATCC 19977 (GCF_000069185.1) | mabscessus ST5, mycobacteria_2 ST5 | mabscessus ST5 | mabscessus ST5 | 100 |
| Mycoplasmopsis bovis PG45 (GCF_000183385.1) | mbovis ST17, mbovis_2 ST12 | mbovis ST17 | mbovis_2 ST12 | 100 |
| Mycoplasmoides gallisepticum (GCF_900476085.1) | mgallisepticum ST23, mgallisepticum_2 ST1 | mgallisepticum ST23 | mgallisepticum_2 ST1 | 100 |
| Pasteurella multocida (GCF_002073255.2) | pmultocida ST124, pmultocida_2 ST8 | pmultocida ST124 | pmultocida_2 ST8 | 100 |
| Streptococcus gallolyticus (GCF_013267695.1) | sbsec ST34, sgallolyticus ST117 | sbsec ST34 | sgallolyticus ST117 | 100 |
| Vibrio parahaemolyticus RIMD 2210633 (GCF_000196095.1) | vibrio ST152, vparahaemolyticus ST3 | vibrio ST152 | vparahaemolyticus ST3 | 100 |
| Vibrio vulnificus NBRC 15645 = ATCC 27562 (GCF_002224265.1) | vibrio ST126, vvulnificus ST3 | vibrio ST126 | vibrio ST126 | 100 |
| Yersinia pseudotuberculosis (GCF_900637475.1) | yersinia ST90, ypseudotuberculosis_achtman_3 ST9 | yersinia ST90 | yersinia ST90 | 100 |
| Yersinia ruckeri (GCF_017498685.1) | yersinia ST44, ypseudotuberculosis_achtman_3 ST276, yruckeri ST33 | yersinia ST44 | yruckeri ST33 | 100 |

## Other scheme called than the one picked for (41)

Each genome was picked from NCBI for one scheme, but typing chose another (or none). This is about the genome choice and overlapping schemes, not a disagreement between the tools.

| Picked for scheme | Genome | Called scheme | ST | Status | Why |
|---|---|---|---|---|---|
| abaumannii | Acinetobacter baumannii (GCF_009035845.1) | abaumannii_2 | ST52 | PERFECT | `abaumannii` is skipped by default (`--exclude`), so the other scheme for this species is used |
| arcobacter | Arcobacter acticola (GCF_013177675.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Arcobacter acticola), so no scheme matches |
| brachyspira | Brachyspira aalborgi (GCF_008016755.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Brachyspira aalborgi), so no scheme matches |
| brachyspira_2 | Brachyspira aalborgi (GCF_008016755.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Brachyspira aalborgi), so no scheme matches |
| brachyspira_3 | Brachyspira aalborgi (GCF_008016755.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Brachyspira aalborgi), so no scheme matches |
| brachyspira_4 | Brachyspira aalborgi (GCF_008016755.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Brachyspira aalborgi), so no scheme matches |
| brachyspira_5 | Brachyspira aalborgi (GCF_008016755.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Brachyspira aalborgi), so no scheme matches |
| diphtheria_3 | Corynebacterium diphtheriae (GCF_001457455.1) | cdiphtheriae | ST26 | PERFECT | Tie with `diphtheria_3` (same score); the first by name is reported |
| ecoli | Escherichia coli O157:H7 str. Sakai (GCF_000008865.2) | ecoli_achtman_4 | ST11 | PERFECT | `ecoli` is skipped by default (`--exclude`), so the other scheme for this species is used |
| halobacteria | Candidatus Halobonum tyrrellensis G22 (GCF_000495475.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Candidatus Halobonum tyrrellensis G22), so no scheme matches |
| klebsiella | Klebsiella pneumoniae subsp. pneumoniae HS11286 (GCF_000240185.1) | ecoli_achtman_4 | ST14464 | PERFECT | Tie with `klebsiella` (same score); the first by name is reported |
| leptospira | Leptospira abararensis (GCF_016918735.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Leptospira abararensis), so no scheme matches |
| leptospira_2 | Leptospira abararensis (GCF_016918735.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Leptospira abararensis), so no scheme matches |
| leptospira_3 | Leptospira abararensis (GCF_016918735.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Leptospira abararensis), so no scheme matches |
| liberibacter | Candidatus Liberibacter africanus PTSAPSY (GCF_001021085.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Candidatus Liberibacter africanus PTSAPSY), so no scheme matches |
| mbovis_2 | Mycoplasmopsis bovis PG45 (GCF_000183385.1) | mbovis | ST17 | PERFECT | Tie with `mbovis_2` (same score); the first by name is reported |
| mgallisepticum_2 | Mycoplasmoides gallisepticum (GCF_900476085.1) | mgallisepticum | ST23 | PERFECT | Tie with `mgallisepticum_2` (same score); the first by name is reported |
| mhominis_3 | Metamycoplasma hominis ATCC 27545 (GCF_000767725.1) | mhominis | - | NOVEL | `mhominis` scores higher than `mhominis_3` for this genome |
| mycobacteria_2 | Candidatus Mycobacterium methanotrophicum (GCF_023515995.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Candidatus Mycobacterium methanotrophicum), so no scheme matches |
| pdamselae | Photobacterium damselae subsp. damselae (GCF_038086725.1) | vibrio | - | BAD | `vibrio` scores higher than `pdamselae` for this genome |
| pmultocida_2 | Pasteurella multocida (GCF_002073255.2) | pmultocida | ST124 | PERFECT | Tie with `pmultocida_2` (same score); the first by name is reported |
| providencia | Candidatus Providencia siddallii (GCF_964026685.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Candidatus Providencia siddallii), so no scheme matches |
| rhodococcus | Rhodococcus (subgen. Prescottella) agglutinans (GCF_004011865.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Rhodococcus), so no scheme matches |
| scanis | Streptococcus equinus (GCF_049393805.1) | sbsec | - | BAD | `sbsec` scores higher than `scanis` for this genome |
| senterica_achtman_2 | Salmonella enterica subsp. enterica serovar Typhimurium str. LT2 (GCF_000006945.2) | salmonella | ST19 | PERFECT | `senterica_achtman_2` is skipped by default (`--exclude`), so the other scheme for this species is used |
| serratia | Serratia aquatilis (GCF_044865145.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Serratia aquatilis), so no scheme matches |
| sgallolyticus | Streptococcus gallolyticus (GCF_013267695.1) | sbsec | ST34 | PERFECT | Tie with `sgallolyticus` (same score); the first by name is reported |
| shewanella | Shewanella abyssi (GCF_023284025.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Shewanella abyssi), so no scheme matches |
| sinorhizobium | Sinorhizobium alkalisoli (GCF_008932245.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Sinorhizobium alkalisoli), so no scheme matches |
| sthermophilus | Streptococcus thermophilus (GCF_903886475.1) | streptothermophilus | ST59 | PERFECT | `streptothermophilus` scores higher than `sthermophilus` for this genome |
| streptomyces | Candidatus Streptomyces philanthi (GCF_059553635.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Candidatus Streptomyces philanthi), so no scheme matches |
| ureaplasma | Ureaplasma canigenitalium ATCC 51252 (GCF_000712165.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Ureaplasma canigenitalium ATCC 51252), so no scheme matches |
| vcholerae_2 | Vibrio cholerae IEC224 (GCF_000250855.1) | vcholerae | ST69 | PERFECT | `vcholerae_2` is skipped by default (`--exclude`), so the other scheme for this species is used |
| vibrio | Vibrio aerogenes (GCF_024346755.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Vibrio aerogenes), so no scheme matches |
| vparahaemolyticus | Vibrio parahaemolyticus RIMD 2210633 (GCF_000196095.1) | vibrio | ST152 | PERFECT | Tie with `vparahaemolyticus` (same score); the first by name is reported |
| vtapetis | Vibrio tapetis subsp. quintayensis (GCF_030409945.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Vibrio tapetis subsp. quintayensis), so no scheme matches |
| vvulnificus | Vibrio vulnificus NBRC 15645 = ATCC 27562 (GCF_002224265.1) | vibrio | ST126 | PERFECT | Tie with `vvulnificus` (same score); the first by name is reported |
| wolbachia | Candidatus Wolbachia massiliensis (GCF_014771645.1) | - | - | NONE | NCBI genome is a species the scheme does not cover (Candidatus Wolbachia massiliensis), so no scheme matches |
| yersinia | Yersinia aldovae 670-83 (GCF_000834395.1) | ypseudotuberculosis_achtman_3 | ST217 | PERFECT | `ypseudotuberculosis_achtman_3` scores higher than `yersinia` for this genome |
| ypseudotuberculosis_achtman_3 | Yersinia pseudotuberculosis (GCF_900637475.1) | yersinia | ST90 | PERFECT | Tie with `ypseudotuberculosis_achtman_3` (same score); the first by name is reported |
| yruckeri | Yersinia ruckeri (GCF_017498685.1) | yersinia | ST44 | PERFECT | Tie with `yruckeri` (same score); the first by name is reported |

## Schemes without a validation genome (0)

None.
