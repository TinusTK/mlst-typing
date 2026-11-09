# Validation, database PubMLST_2026-11

Run 2026-11-09: 168 genomes listed (one public NCBI assembly per scheme + priority organisms).

- Typed: 168 (0 without a genome)
- Called the scheme the genome was picked for: 127/168
- PERFECT (full ST): 119/168
- Same result as upstream mlst on the same database: **159/168**
- Ties (two schemes with the same top score; mlst picks one at random, mlst-typing the first by name): 9/168
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

## Ties (both tools agree on the score; scheme choice differs) (9)

- GCF_001457455.1 (cdiphtheriae): mlst-typing cdiphtheriae ST26 / mlst diphtheria_3 ST26 (score 100)
- GCF_001457455.1 (diphtheria_3): mlst-typing cdiphtheriae ST26 / mlst diphtheria_3 ST26 (score 100)
- GCF_000240185.1 (klebsiella): mlst-typing ecoli_achtman_4 ST14464 / mlst klebsiella ST11 (score 100)
- GCF_000069185.1 (mabscessus): mlst-typing mabscessus ST5 / mlst mycobacteria_2 ST5 (score 100)
- GCF_900476085.1 (mgallisepticum_2): mlst-typing mgallisepticum ST23 / mlst mgallisepticum_2 ST1 (score 100)
- GCF_002073255.2 (pmultocida): mlst-typing pmultocida ST124 / mlst pmultocida_2 ST8 (score 100)
- GCF_002073255.2 (pmultocida_2): mlst-typing pmultocida ST124 / mlst pmultocida_2 ST8 (score 100)
- GCF_000196095.1 (vparahaemolyticus): mlst-typing vibrio ST152 / mlst vparahaemolyticus ST3 (score 100)
- GCF_002224265.1 (vvulnificus): mlst-typing vibrio ST126 / mlst vvulnificus ST3 (score 100)

## Other scheme called than the one picked for (41)

- abaumannii: GCF_009035845.1 Acinetobacter baumannii -> abaumannii_2 52 PERFECT
- arcobacter: GCF_013177675.1 Arcobacter acticola -> - - NONE
- brachyspira: GCF_008016755.1 Brachyspira aalborgi -> - - NONE
- brachyspira_2: GCF_008016755.1 Brachyspira aalborgi -> - - NONE
- brachyspira_3: GCF_008016755.1 Brachyspira aalborgi -> - - NONE
- brachyspira_4: GCF_008016755.1 Brachyspira aalborgi -> - - NONE
- brachyspira_5: GCF_008016755.1 Brachyspira aalborgi -> - - NONE
- diphtheria_3: GCF_001457455.1 Corynebacterium diphtheriae -> cdiphtheriae 26 PERFECT
- ecoli: GCF_000008865.2 Escherichia coli O157:H7 str. Sakai -> ecoli_achtman_4 11 PERFECT
- halobacteria: GCF_000495475.1 Candidatus Halobonum tyrrellensis G22 -> - - NONE
- klebsiella: GCF_000240185.1 Klebsiella pneumoniae subsp. pneumoniae HS11286 -> ecoli_achtman_4 14464 PERFECT
- leptospira: GCF_016918735.1 Leptospira abararensis -> - - NONE
- leptospira_2: GCF_016918735.1 Leptospira abararensis -> - - NONE
- leptospira_3: GCF_016918735.1 Leptospira abararensis -> - - NONE
- liberibacter: GCF_001021085.1 Candidatus Liberibacter africanus PTSAPSY -> - - NONE
- mbovis_2: GCF_000183385.1 Mycoplasmopsis bovis PG45 -> mbovis 17 PERFECT
- mgallisepticum_2: GCF_900476085.1 Mycoplasmoides gallisepticum -> mgallisepticum 23 PERFECT
- mhominis_3: GCF_000767725.1 Metamycoplasma hominis ATCC 27545 -> mhominis - NOVEL
- mycobacteria_2: GCF_023515995.1 Candidatus Mycobacterium methanotrophicum -> - - NONE
- pdamselae: GCF_038086725.1 Photobacterium damselae subsp. damselae -> vibrio - BAD
- pmultocida_2: GCF_002073255.2 Pasteurella multocida -> pmultocida 124 PERFECT
- providencia: GCF_964026685.1 Candidatus Providencia siddallii -> - - NONE
- rhodococcus: GCF_004011865.1 Rhodococcus (subgen. Prescottella) agglutinans -> - - NONE
- scanis: GCF_049393805.1 Streptococcus equinus -> sbsec - BAD
- senterica_achtman_2: GCF_000006945.2 Salmonella enterica subsp. enterica serovar Typhimurium str. LT2 -> salmonella 19 PERFECT
- serratia: GCF_044865145.1 Serratia aquatilis -> - - NONE
- sgallolyticus: GCF_013267695.1 Streptococcus gallolyticus -> sbsec 34 PERFECT
- shewanella: GCF_023284025.1 Shewanella abyssi -> - - NONE
- sinorhizobium: GCF_008932245.1 Sinorhizobium alkalisoli -> - - NONE
- sthermophilus: GCF_903886475.1 Streptococcus thermophilus -> streptothermophilus 59 PERFECT
- streptomyces: GCF_059553635.1 Candidatus Streptomyces philanthi -> - - NONE
- ureaplasma: GCF_000712165.1 Ureaplasma canigenitalium ATCC 51252 -> - - NONE
- vcholerae_2: GCF_000250855.1 Vibrio cholerae IEC224 -> vcholerae 69 PERFECT
- vibrio: GCF_024346755.1 Vibrio aerogenes -> - - NONE
- vparahaemolyticus: GCF_000196095.1 Vibrio parahaemolyticus RIMD 2210633 -> vibrio 152 PERFECT
- vtapetis: GCF_030409945.1 Vibrio tapetis subsp. quintayensis -> - - NONE
- vvulnificus: GCF_002224265.1 Vibrio vulnificus NBRC 15645 = ATCC 27562 -> vibrio 126 PERFECT
- wolbachia: GCF_014771645.1 Candidatus Wolbachia massiliensis -> - - NONE
- yersinia: GCF_000834395.1 Yersinia aldovae 670-83 -> ypseudotuberculosis_achtman_3 217 PERFECT
- ypseudotuberculosis_achtman_3: GCF_900637475.1 Yersinia pseudotuberculosis -> yersinia 90 PERFECT
- yruckeri: GCF_017498685.1 Yersinia ruckeri -> yersinia 44 PERFECT

## Schemes without a validation genome (0)

None.
