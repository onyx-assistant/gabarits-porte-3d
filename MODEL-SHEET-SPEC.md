# Feuille de modèle Onyx — Spécification (phase 3D-0)

**Statut : APPROUVÉ — pack canonique 3D v1. Validé par l'atelier le 21 novembre 2026 (porte nº 1 franchie) : la feuille de modèle et le corps entier lui conviennent tels quels. Optimisations possibles plus tard, mais pour l'instant, c'est final. Les vues retenues et les planches sont copiées dans `00_canonical/3d-v1/` avec manifeste SHA-256.**
Date : 21 novembre 2026. Dossier : `<racine-du-projet>/3d/model-sheet/`.
Source unique : la référence canonique de face (`references/onyx-canonique.webp`, MD5 `2615852ff83d36e6468342cfbd5c8a8b8` ; mesures prises sur la copie PNG `assets/onyx-reference.png`, 1600×1600). Toutes les autres vues sont des **inventions raisonnées** générées à partir de cette référence, puis choisies et assemblées.

---

## 0. Destination de cette feuille

Cette feuille est la **fondation de conception de tout le personnage**, pas un simple support d'images :

- référence de modélisation 3D du volet Unreal (sculpt, matériau tissu, proportions) ;
- base de la description officielle du personnage (posts, réseaux sociaux, sites, page GitHub) ;
- à terme, référence d'une présence 3D **debout, en direct**, dans des conversations vidéo.

Conséquence appliquée partout ci-dessous : les inventions (profil, dos, bas du corps) privilégient la **cohérence volumique** — des volumes qui doivent « tenir » en 3D sous tous les angles — plutôt que la seule apparence à plat. Les proportions debout sont mesurées, stables, et les planches partagent une échelle constante et une ligne de sol commune.

---

## 1. Conventions de mesure

- **T** = hauteur de tête, du **sommet du crâne** au **menton** (convention de la charte graphique v0.2). Sur la référence : crâne y = 332, menton y ≈ 1135 → **1 T = 803 px**.
- **LT** = largeur maximale de la tête (sans les oreilles) : **937 px = 1,17 T**, atteinte à y ≈ 800.
- Axe de symétrie : x ≈ 800 (la couture centrale « marche » de ±15 px, fait normal d'une peluche photographiée).
- Mesures programmatiques (PIL/numpy/scipy) complétées visuellement pour les éléments sans détection fiable (museau, bouche).

### Réconciliation avec la charte v0.2 (§7)

La charte annonce provisoirement « buste visible ≈ 1,4 T ». Avec la convention T ci-dessus, le buste visible de la référence mesure **1,67 T**. Les deux chiffres sont compatibles : 1,4 T s'obtient avec une hauteur de tête « oreilles comprises, jusqu'au cou » (≈ 960 px). **À trancher à la porte nº 1 : quelle définition de T devient la convention permanente.** Ce document utilise partout T = crâne → menton.

---

## 2. Mesures sur la référence canonique (face, buste)

Silhouette : x 264..1325, y 258..1599 (le bas est coupé par le cadre — c'est un buste). Hauteur visible : 1342 px = **1,67 T**.

| Repère | Mesure (px, image 1600×1600) | En unités |
|---|---|---|
| Sommet des oreilles | y 258 (droite) / 268 (gauche) — asymétrie réelle ≈ 10 px | 0,09 T au-dessus du crâne |
| Sommet du crâne | y 332 (bande centrale) | 0 (origine de T) |
| Oreilles | largeur ≈ 175–190 px chacune ; bases ≈ y 395 | largeur ≈ 0,19 LT |
| Largeur max. de la tête | 937 px à y ≈ 800 | 1,00 LT = 1,17 T |
| Sourcils | longueur ≈ 100 px ; centres ≈ (630, 515) et (982, 511) | 0,11 LT ; à 0,23 T sous le crâne |
| Yeux | G : centre (655, 690), 83×138 px ; D : centre (970, 686), 82×126 px | h ≈ 0,14 LT ; **rapport h/l ≈ 1,6** |
| Entraxe des yeux | 315 px | **0,34 LT** |
| Centres des yeux | y ≈ 688 | à **0,44 T** sous le sommet du crâne |
| Museau (zone, estimation visuelle) | ≈ x 690..960, y 690..930 ; centre ≈ (810, 830) | relief doux, sans nez dessiné |
| Bouche (sourire) | largeur ≈ 370 px ; coins ≈ y 878 ; point bas de l'arc ≈ (815, 930) | **0,40 LT** ; bas à 0,74 T sous le crâne |
| Couture centrale | x ≈ 800–815 (front ≈ 828, torse ≈ 814) | axe du personnage |
| Menton / pincement du cou | y ≈ 1135 ; largeur minimale 584 px à y ≈ 1131 | 1,00 T ; cou = 0,62 LT |
| Épaules | la largeur repart à la hausse dès y ≈ 1180 | 1,06 T sous le crâne |
| Torse au bas du cadre | ≈ 1049 px bras compris (≈ 960 px torse seul, estimé) | ≈ 1,12 LT bras compris |

Couleurs échantillonnées sur la photo (variables avec l'éclairage — **la charte fait foi** : lumière #FC8B32, médian #C95D1D, ombre #8D2E0F) : front éclairé #F4741E, joue en mi-ombre #AA4716, torse #D35B17.

### Écarts avec les valeurs d'orientation du PLAN-3D (§0)

- Yeux : rapport hauteur/largeur mesuré **1,6** (plan : ~2). Les yeux sont moins « grains de riz » qu'estimé.
- Entraxe des yeux : **0,34 LT** (plan : ~0,28 LT).
- Sourire : 0,40 LT — conforme au plan.
- Ces mesures-ci, prises sur la référence elle-même, priment sur les orientations du plan.

---

## 3. Corps entier debout — proposition de proportions

**Hauteur totale proposée : 2,5 T** (sol → sommet du crâne : 2,42 T ; sommet des oreilles : 2,51 T).
Mesurée sur le candidat de face retenu : **2,51 T** ; fourchette des candidats générés : 2,26–2,61 T. La tête (crâne → menton) représente **40 %** de la hauteur totale.

Décomposition depuis le sol (arrondie, à figer à la porte nº 1) :

| Segment | Hauteur |
|---|---|
| Pieds + jambes (sol → base du ventre/hanches) | 0,55 T |
| Torse sous le menton (hanches → menton) | 0,87 T |
| Tête (menton → sommet du crâne) | 1,00 T |
| Oreilles (au-dessus du crâne) | + 0,09 T |
| **Total (sommet des oreilles)** | **≈ 2,51 T** |

Justification :
- Proportions d'ourson en peluche trapu et doux, cohérentes avec la tête énorme de la référence (1,17 T de large) : en dessous de ~2,3 T le personnage paraîtrait écrasé ; au-dessus de ~2,7 T il perdrait le côté peluche compacte.
- Cohérence avec le buste canonique : le bas du cadre de la référence tombe à 0,84 T au-dessus du sol dans cette échelle, c'est-à-dire dans le tiers supérieur du ventre (les hanches sont à ≈ 0,62 T) — exactement là où la référence montre le torse encore en train de s'élargir. Aucune contradiction entre le buste connu et le bas inventé.

Design du bas du corps (inventé) : ventre rond qui prolonge le torse sans rupture ; couture centrale qui descend du menton au bas du ventre et passe entre les jambes ; jambes courtes et rondes ; pieds ronds et ovales, sans doigts, sans coussinets, sans semelle dessinée ; aucun vêtement, aucune queue. Bras le long du corps, mains en moufles sans doigts (comme le suggère le bas du cadre de la référence).

---

## 4. Candidats générés et choix retenus

Génération par édition d'image à partir de la référence canonique (et, pour le corps entier, à partir des vues retenues). Fichiers d'origine `media-generation-*.webp` conservés dans ce dossier ; copies PNG aux noms propres ci-dessous.

| Vue | Retenu | Choix et raison |
|---|---|---|
| Face (buste) | `vue-face-buste-canonique.png` | **La référence canonique elle-même**, non régénérée (copie de `assets/onyx-reference.png`). |
| Trois-quarts (buste) | `vue-trois-quarts-buste.png` | Un seul candidat nécessaire : les deux oreilles et les deux yeux lisibles, sourcils et sourire présents, couture du torse visible, volume du museau crédible. Réserve mineure : sourire un peu large. |
| Profil (buste) | `vue-profil-buste.png` (cand. 2) | Tête énorme posée **directement sur le torse, sans cou** (conforme à la référence), couture passant sur le dessus de la tête, œil et sourcil en place. **Réserve importante : profondeur du museau au bout « profond » de la fourchette plausible** — voir §5. |
| Profil (buste), alternative | `vue-profil-buste-alt.png` (cand. 1) | Museau plus plat, mais **cou visible** et tête proportionnellement plus petite, torse trop long : contredit la référence. Conservé uniquement comme borne « museau plat » pour l'arbitrage de la porte nº 1. |
| Dos (buste) | `vue-dos-buste.png` | Tête ronde, deux oreilles rondes, **couture centrale tête → dos → torse alignée avec la couture avant**, bras le long du corps, pas de queue. Réserve mineure : oreilles légèrement « pompon ». |
| Face corps entier | `vue-face-corps-entier.png` (cand. 2) | Jambes **courtes et rondes**, pieds ronds « peluche », ventre en œuf doux, hauteur mesurée 2,51 T. Le plus cohérent avec le haut et avec le design du §3. |
| Face corps entier, alternative | `vue-face-corps-entier-alt.png` (cand. 1) | Jambes plus longues et droites, pieds structurés « en chaussure » avec ligne de semelle ; hauteur 2,60 T. Conservé pour comparaison. |
| Profil corps entier | `vue-profil-corps-entier.png` | Même tête que le profil buste retenu, ventre rond en profil, couture continue. Réserves : pied long (type chaussure) et main avec début de pouce — à harmoniser au sculpt, voir §5. |
| Dos corps entier | `vue-dos-corps-entier.png` | Couture continue du sommet de la tête jusqu'entre les jambes, talons ronds, aucun ajout. Cohérent avec le dos buste. |

---

## 5. Règles d'invention appliquées et limites connues

Règles suivies pour toutes les vues inventées : volumes simples et fermés (qui tiennent en 3D) ; aucune caractéristique absente de la face (pas de nez, pas de narines, pas de queue, pas de doigts/orteils, pas de coussinets) ; oreilles = disques ronds épais vus sous tous les angles ; la couture est **une seule ligne continue** qui fait le tour du personnage par le plan de symétrie (dessus de tête → face → ventre → entre-jambes → dos → arrière de tête) ; pas de cou : la tête fusionne avec le torse par un pincement doux (0,62 LT au plus étroit).

Limites connues, à connaître avant validation :

1. **Profondeur du museau (point d'arbitrage nº 1).** De face, le museau n'est qu'un ombrage : sa profondeur réelle est indécidable depuis la seule référence. Le profil retenu le dessine plutôt profond (petit museau saillant avec une fente de bouche dessous) ; l'alternative le dessine plat mais avec un cou fautif. Il faudra trancher une profondeur cible — le sculpt 3D pourra tester les deux à peu de frais.
2. **Bouche de profil.** Dans les deux candidats, la bouche de profil devient une fente sous le museau, alors que de face c'est un trait posé sur la surface. En 3D, la bouche restera un trait de surface ; le profil final devra s'y conformer.
3. **Normalisation des planches.** Les vues générées n'ont pas exactement la même coupe de torse ni le même cadrage : les planches sont normalisées par hauteur de silhouette. Les lignes de repère sont **exactes pour la vue de face** et indicatives (± ~3 %) pour les vues inventées.
4. **Asymétries de peluche.** Oreille droite ~10 px plus haute que la gauche sur la référence ; les vues générées ont leurs propres micro-asymétries. À la modélisation, on visera une symétrie propre en gardant l'esprit « peluche réelle ».
5. **Pieds et mains du profil corps entier** : pied plus long et main avec ébauche de pouce, hérités de la génération ; le design cible reste « pied rond court, main moufle » (vue de face corps entier retenue).
6. **Fonds des vues corps entier** : légère ombre de contact au sol (le fond n'est pas blanc pur en bas d'image). Sans impact sur la modélisation ; à nettoyer si ces images servent un jour de visuels publics.
7. **Couleurs** : les vues générées respectent la famille orange de la charte à l'œil, sans garantie d'échantillonnage exact ; la matière 3D se réglera sur les hex de la charte, pas sur ces images.

---

## 6. Ce que l'atelier doit valider à la porte nº 1

**Résolution — porte nº 1 franchie le 21 novembre 2026.** l'atelier a approuvé la feuille telle que présentée (« je suis en accord avec la feuille de modèle et le corps entier » ; « on pourra toujours l'optimiser, mais pour l'instant, c'est final »), puis a élevé les vues trois-quarts, profil et dos (buste et corps entier) au rang de références canoniques. En conséquence : profil retenu tel quel (point 1), dos approuvé (2), hauteur 2,5 T et décomposition approuvées (3), bas du corps approuvé (4), convention T = crâne → menton adoptée comme permanente (5), trois-quarts accepté (6). Les questions ci-dessous restent le libellé historique de la porte.

1. **Profondeur du museau** en profil : plutôt profond (profil retenu), plutôt plat (borne alternative), ou entre les deux ?
2. **Le dos** : couture dorsale unique alignée sur la couture avant, oreilles vues de dos, absence de queue — approuvé ?
3. **Hauteur totale 2,5 T** et décomposition du §3 — approuvées ? (Alternatives vues : 2,60 T jambes plus longues.)
4. **Bas du corps** : ventre rond, jambes courtes, pieds ronds sans semelle ni coussinets, couture entre les jambes — approuvé ?
5. **Convention T** : crâne → menton (ce document) ou oreilles → cou (charte v0.2, « 1,4 T ») comme définition permanente ?
6. **Trois-quarts** : sourire un peu large — acceptable comme brouillon de travail ?
7. Après validation : ces vues deviennent le **pack canonique 3D v1** (copie dans `00_canonical/` avec manifeste SHA-256), et la charte passe en v0.3 avec les proportions figées.

---

## 7. Inventaire des fichiers (ce dossier)

Planches assemblées (montage PIL, échelle constante, lignes de repère) :
- `planche-buste.png` — face (canonique), trois-quarts, profil, dos ; repères : oreilles, crâne, base des oreilles, sourcils, yeux, museau, bouche, menton, épaules, base du torse.
- `planche-corps-entier.png` — face, profil, dos debout ; ligne de sol commune, aplombs verticaux (face et dos), échelle en T à droite (0 → 2,5 T).

Vues retenues (copies PNG) : `vue-face-buste-canonique.png`, `vue-trois-quarts-buste.png`, `vue-profil-buste.png`, `vue-dos-buste.png`, `vue-face-corps-entier.png`, `vue-profil-corps-entier.png`, `vue-dos-corps-entier.png`.
Alternatives conservées : `vue-profil-buste-alt.png`, `vue-face-corps-entier-alt.png`.
Fichiers sources de génération : `media-generation-*.webp` (+ leurs `.json` de génération).

**Rappel de statut : APPROUVÉ le 21 novembre 2026 — pack canonique 3D v1 dans `00_canonical/3d-v1/` (manifeste SHA-256). Rien n'a été publié ni envoyé.**
