---
language:
- fr
license: mit
---

# gabarits-porte-3d — mesurer le modèle 3D avant de le croire

La voie 3D de l'atelier fabrique un modèle d'Onyx (la peluche orange
virtuelle de Montréal) utilisable partout : vidéo produite, temps réel,
jeux. Mais un modèle généré « qui a l'air bien » ne suffit pas — il doit
**passer la porte** : les mêmes mesures, à chaque itération, avec des
seuils écrits d'avance.

Ce dépôt contient les gabarits de mesure de la porte 3D et les scripts de
test d'armature qui l'accompagnent.

## `mesurer_porte.py` — le gabarit de mesure

Un script Blender en mode sans interface (`blender --background`) qui, sur
un modèle candidat, mesure :

- les **proportions** normalisées (hauteur totale H comme unité : largeur
  de tête / H, entraxe des yeux / H, hauteurs de segments…) ;
- les **écarts au modèle de référence** de la charte, en pourcentage ;
- la **couleur** moyenne des zones du pelage, comparée à la charte en ΔE.

Seuils de la porte stricte (étape de validation du plan de l'atelier) :
**proportions ≤ 3 %, traits ≤ 2 %, couleurs conformes à la charte**. Un
candidat qui échoue reste un brouillon — c'est arrivé, et c'est le
fonctionnement normal : le premier brouillon mesuré échouait sur la largeur
des jambes (−13 %) et la couleur (ΔE 13,5), ce que l'œil seul n'avait pas
quantifié.

```bash
blender --background --python mesurer_porte.py -- \
  --input modele-candidat.glb --outdir mesures/
```

La fiche de mesure complète — définitions des mesures, constantes,
tolérances et leur statut — est dans
[`FICHE-MESURE-PORTE.md`](FICHE-MESURE-PORTE.md).

## `MODEL-SHEET-SPEC.md` — la fiche modèle

La spécification des vues de référence du personnage (face, profil, dos,
trois-quarts ; buste et corps entier) dont tout modèle 3D doit partir :
cadrages, proportions en unités T (hauteur de tête), et règles de
cohérence entre vues. Les images de référence elles-mêmes ne sont pas
publiées : ce sont les fichiers maîtres du personnage.

## `test_armature.py` et `planches.py` — le test d'armature jetable

Avant de confier le modèle définitif à un squelette, l'atelier a testé
l'armature sur un **brouillon jetable** : génération d'un squelette aux noms
normalisés (convention VRM, plus les oreilles `onyx_ear.L/R`), skinning,
poses témoins, et planches de contrôle. Verdict consigné : le skinning par
« bone heat » échoue silencieusement sur ce type de maillage ; le repli
retenu est un skinning par enveloppes sur armature réduite (20 os), qui a
donné **0 sommet sans poids**. Les scripts sont ici ; le maillage de test,
lui, n'est pas publié.

## Place dans la chaîne de l'atelier

La porte 3D est le pendant, pour la géométrie, de la porte de fidélité des
images (dépôt `porte-fidelite`). Le plan complet de la voie 3D — étapes 0 à
6, de la fiche modèle au modèle passé à la porte stricte — est documenté
dans le dépôt `documentation-atelier` (`PLAN-VOIE-3D-V1.md`).

## Licence

Code et documentation sous licence MIT (voir `LICENCE.md`). Le personnage
Onyx, ses vues de référence et ses modèles restent la propriété de
l'atelier et ne sont pas inclus.
