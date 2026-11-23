# Fiche de mesure — Porte stricte 3D (gabarit, étape 2 du plan)

_Créée le 22 novembre 2026. Voie 3D, `docs/PLAN-VOIE-3D-V1.md` **étape 2 — Gabarits de mesure de la porte**. Cette fiche fige **les grandeurs, les références, les seuils et les conventions de repère** qui serviront à chaque passe de resculpt (étape 4) et au test formel de la porte (étape 5). Mêmes mesures, mêmes seuils, aucun jugement « à l'œil » non chiffré._

_Outil associé : `mesurer_porte.py` (même dossier) — Blender **headless** (testé sous Blender 5.2.4 LTS sur Fractal). Aucun écran de l'atelier requis._

---

## 1. Références canoniques (sources des cibles)

| Référence | Rôle |
|---|---|
| `3d/model-sheet/MODEL-SHEET-SPEC.md` — pack canonique 3D v1, approuvé par l'atelier le 21 nov. 2026 (porte nº 1) | **Source unique des cibles chiffrées** (§ 2 mesures sur la référence de face, § 3 corps entier figé) |
| `references/onyx-canonique.webp` (MD5 `2615852ff83d36e6468342cfbd5c8a8b8`) ; copie de travail `assets/onyx-reference.png` | Référence maîtresse de face, sur laquelle la spec a été mesurée |
| `tests/ltx-flat-eric-groove/onyx-i2v-input-3q-1088x1920.png` (MD5 `86158194db00f40309b0fb26e2598538`) | Vue trois-quarts canonique (entrée de référence des chaînes de production) |
| `00_canonical/3d-v1/` (vues retenues + manifeste SHA-256) | Vues canoniques trois-quarts / profil / dos, buste et corps entier |
| `docs/CHARTE-GRAPHIQUE.md` § 3 | Palette : lumière `#FC8B32`, médian `#C95D1D`, ombre `#8D2E0F` |

## 2. Conventions de repère (figées par ce gabarit)

- **T** = hauteur de tête, du **sommet du crâne** au **menton** (convention permanente, porte nº 1).
- **Le menton = le pincement du cou** : la spec § 2 les donne comme un seul repère (« Menton / pincement du cou »). Le gabarit le localise comme le **minimum du profil de largeur lissé** (moyenne mobile 5, 256 bandes de hauteur) dans la zone 0,40 H – 0,72 H. Si la largeur au pincement n'est pas < 85 % du min(largeur de tête, largeur de torse), le pincement est déclaré **non net** et les mesures qui en dépendent sont marquées **fiabilité FAIBLE**.
- **H** = hauteur totale, sol → sommet des oreilles = **2,51 T**. **LT** = largeur maximale de la tête = **1,17 T**.
- Sommet du crâne = sommet des sommets **centraux** (|x − centre| ≤ 0,18 LT estimée), pour exclure les oreilles, latérales. Sommet des oreilles = sommet global.
- Sens du visage détecté automatiquement (protrusion maximale dans la bande 0,55 H – 0,85 H, comme au test d'armature).
- Échelle en T des rendus : caméra orthographique, `ortho_scale = 1,30 H`, cadrage centré à 0,50 H — identique à chaque passe.

## 3. Grandeurs mesurées et seuils

### 3.1 Proportions — seuil ≤ 3 % (écart relatif à la cible)

| # | Grandeur (ratio) | Cible | Source |
|---|---|---|---|
| P1 | Hauteur de tête / H | 0,3984 (1,00 T / 2,51 T) | spec § 3 |
| P2 | Largeur max de tête / H | 0,4661 (1,17 T / 2,51 T) | spec § 2–3 |
| P3 | Largeur max de tête / T (LT/T) | 1,17 | spec § 2 |
| P4 | Largeur au pincement du cou / LT | 0,62 | spec § 2 |
| P5 | Hauteur du menton / H | 0,5657 (1,42 T / 2,51 T) | spec § 3 (jambes 0,55 T + torse 0,87 T) |
| P6 | Jambes + pieds / H | 0,2191 (0,55 T / 2,51 T) | spec § 3 — mesuré sur le rendu de face (encoche inter-jambes) |
| P7 | Envergure max (bras/torse) / H | 0,537 | référence mesurée (test Pixal3D, méthode validée sur la référence) |
| P8 | Dépassement des oreilles au-dessus du crâne / T | 0,09 | spec § 2–3 |

### 3.2 Traits — seuil ≤ 2 %

| # | Grandeur (ratio) | Cible | Source |
|---|---|---|---|
| T1 | Entraxe des yeux / LT | 0,34 | spec § 2 |
| T2 | Hauteur d'œil / LT | 0,14 | spec § 2 |
| T3 | Ratio hauteur/largeur de l'œil | 1,6 | spec § 2 |
| T4 | Centre des yeux sous le sommet du crâne / T | 0,44 | spec § 2 |
| T5 | Longueur de sourcil / LT | 0,1067 (≈100 px / 937 px) | spec § 2 |

Traits mesurés sur le **rendu orthographique de face** : silhouette par le canal alpha (film transparent), traits = composants connexes sombres (luminance < 0,22) dans la zone du visage délimitée par la géométrie (menton → crâne). Les deux yeux = la paire de composants la plus symétrique en taille et en hauteur.

### 3.3 Couleurs — charte

- Échantillonnage sur la **texture base couleur** du modèle (jamais sur les rendus : l'éclairage est exclu), médiane RGB des texels orangés.
- Distances **ΔE76 (CIE Lab)** de la médiane contre les trois oranges de la charte.
- **Tolérance retenue par ce gabarit : ΔE76 ≤ 5,0 contre l'orange médian `#C95D1D`** — *provisoire* : le plan dit « couleurs de la charte (ΔE dans la tolérance de la porte) » sans figer le chiffre ; 5,0 est cohérent avec la porte qualité images du projet (ΔE ≈ 5 accepté) et très en dessous des 9–15 des brouillons Pixal3D, « nettement visibles ». **À confirmer par l'atelier au premier verdict de porte** ; si le chiffre change, il change ici et dans le script (constante `SEUIL_DELTAE`), jamais en cours de passe.

### 3.4 Mesures hors verdict (assumées)

| Grandeur | Statut | Raison |
|---|---|---|
| Largeur de bouche / LT (cible 0,40) | **Indicative seulement** | La détection automatique de la bouche a été **invalidée aussi sur la référence** lors du test Pixal3D (l'ombre du museau fausse le seuillage). Le gabarit rapporte le chiffre quand il le trouve, marqué INDICATIF ; le verdict bouche de la porte reste **visuel, côte à côte**. |
| Profondeur / protrusion du museau | **Informative seulement** | La spec ne fige **aucun chiffre** (porte nº 1 : profil retenu « plutôt profond », sans cible). Le gabarit rapporte la protrusion brute de la bande du museau ; une cible pourra être figée au premier verdict de porte à partir du modèle jugé bon. |

## 4. Exécution du gabarit

```
blender -b --python mesurer_porte.py -- --input <modele.glb> --outdir <dossier-de-passe>
```

Sorties dans le dossier de passe : `mesures-porte.json` (toutes les mesures, écarts %, verdicts partiels et global, mentions de fiabilité), `rendu-face.png`, `rendu-profil.png`, `rendu-dos.png` (900 × 1260, orthographiques), `FIN.txt` (ou `ERREUR.txt`).

Le verdict global du script vaut PASS seulement si **toutes** les grandeurs à verdict sont PASS (une grandeur NON MESURABLE fait échouer le global : à la porte, ne pas pouvoir mesurer = ne pas pouvoir passer).

## 5. Où le verdict de porte sera consigné (étape 5)

1. **Dossier de passe daté** par candidat, sous `3d/` (ex. `3d/porte-AAAA-MM-JJ-<candidat>/`) : le `mesures-porte.json` + les trois rendus du gabarit, intacts.
2. **Verdict formel PASS/FAIL de l'atelier** : `docs/JOURNAL-DECISIONS.md` + ligne du **backlog nº 8** (règle du plan § 2, étape 5). Le verdict du script ne remplace jamais celui de l'atelier : le script chiffre, l'atelier tranche sur le côte à côte.
3. Tant que la porte n'est pas PASS : retour au resculpt (étape 4), **les seuils ne se desserrent pas**.

## 6. Validation du gabarit lui-même

Test à blanc sur le brouillon Pixal3D SV (jetable) le 22 nov. 2026 : voir `test-brouillon-sv/RAPPORT-TEST-GABARIT.md` (même dossier parent). Le brouillon échoue à la porte — résultat attendu ; c'est l'**outil** qui était testé, pas le modèle. Contre-vérifications contre le test Pixal3D du même jour : largeur de tête, envergure, entraxe des yeux et couleur médiane **reproduits à l'identique ou au plus proche** par des chaînes indépendantes.
