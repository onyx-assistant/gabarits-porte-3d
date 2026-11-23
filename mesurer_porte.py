# Gabarit de mesure de la PORTE STRICTE 3D -- Blender headless
# Voie 3D, etape 2 du PLAN-VOIE-3D-V1 (gabarits de mesure).
#
# Mesure un modele candidat (GLB) contre les cibles figees de
# 3d/model-sheet/MODEL-SHEET-SPEC.md (pack canonique 3D v1, porte no 1,
# 21 nov. 2026) et la palette de la charte (docs/CHARTE-GRAPHIQUE.md S3).
#
# Seuils de la porte (PLAN-VOIE-3D-V1 S1/S2) :
#   proportions <= 3 %, traits <= 2 %, couleurs = charte (DeltaE76).
# Tolérance DeltaE retenue pour ce gabarit : <= 5,0 sur la mediane contre
# l'orange median de la charte (provisoire, a confirmer au premier verdict
# de porte ; les brouillons Pixal3D mesuraient 9-15, nettement visibles).
#
# Usage :
#   blender -b --python mesurer_porte.py -- --input <modele.glb> --outdir <dossier>
# Sans arguments : brouillon Pixal3D SV de Fractal + dossier par defaut.
#
# Sorties dans --outdir :
#   mesures-porte.json   (toutes les mesures, ecarts, verdicts partiels)
#   rendu-face.png / rendu-profil.png / rendu-dos.png (orthographiques)
#   FIN.txt (PASS-GABARIT / ECHEC) ou ERREUR.txt
#
# Methodes (meme esprit que le test Pixal3D du 22 nov. 2026, qui avait
# valide la methode sur la reference canonique) :
#   - geometrie directe sur les sommets (profil de largeur en bandes de Z) ;
#   - analyse d'image sur les rendus orthographiques (silhouette, blobs
#     sombres pour les yeux) ;
#   - echantillonnage de la texture base couleur (jamais les rendus, pour
#     exclure l'eclairage).
# Limites assumees et documentees dans la fiche associee :
#   - bouche : detection automatique NON fiable (invalidee aussi sur la
#     reference lors du test Pixal3D) -> mesure indicative seulement,
#     exclue du verdict automatique ;
#   - profondeur du museau : aucune cible numerique figee dans la spec
#     (point d'arbitrage de la porte no 1 tranche "plutot profond" sans
#     chiffre) -> mesure informative seulement, sans verdict.
import bpy
import json
import math
import os
import sys
import traceback

import numpy as np

# ---------------------------------------------------------------- args
argv = sys.argv
args = argv[argv.index("--") + 1:] if "--" in argv else []


def arg_val(nom, defaut):
    if nom in args:
        i = args.index(nom)
        if i + 1 < len(args):
            return args[i + 1]
    return defaut


SRC = arg_val("--input", r"C:\Users\<utilisateur>\ComfyUI\output\3d\pixal3d_sv_onyx_00001.glb")
OUTDIR = arg_val("--outdir", r"C:\Users\<utilisateur>\onyx-3d\gabarit-porte")

os.makedirs(OUTDIR, exist_ok=True)
R = {"script": "mesurer_porte.py v1.1 (2026-11-22)", "source": SRC}


def log(msg):
    print("[PORTE] " + str(msg), flush=True)


# ---------------------------------------------------------------- cibles
# Toutes les cibles sont des ratios sans dimension, tires de
# MODEL-SHEET-SPEC.md S2 (mesures sur la reference canonique de face) et
# S3 (corps entier fige : total 2,51 T oreilles comprises, T = crane->menton).
#   T  = hauteur de tete (crane -> menton) ; LT = largeur max de tete = 1,17 T
#   H  = hauteur totale (sol -> sommet des oreilles) = 2,51 T
CIBLES_PROP = [
    # (cle, libelle, cible, source)
    ("tete_sur_H", "Hauteur de tete / hauteur totale", 1.00 / 2.51, "spec S3 : tete = 1,00 T sur 2,51 T (40 %)"),
    ("largeur_tete_sur_H", "Largeur max de tete / hauteur totale", 1.17 / 2.51, "spec S2/S3 : LT = 1,17 T"),
    ("largeur_tete_sur_T", "Largeur max de tete / hauteur de tete (LT/T)", 1.17, "spec S2 : LT = 1,17 T"),
    ("pincement_sur_largeur_tete", "Largeur min au cou / largeur de tete", 0.62, "spec S2 : pincement du cou = 0,62 LT"),
    ("menton_sur_H", "Hauteur du menton (pincement) / hauteur totale", (0.55 + 0.87) / 2.51, "spec S3 : jambes 0,55 T + torse 0,87 T"),
    ("jambes_sur_H", "Jambes + pieds / hauteur totale", 0.55 / 2.51, "spec S3 : 0,55 T"),
    ("envergure_sur_H", "Envergure max (bras/torse) / hauteur totale", 0.537, "reference mesuree (test Pixal3D, methode validee sur la reference)"),
    ("oreilles_au_dessus_crane_sur_T", "Depassement des oreilles / hauteur de tete", 0.09, "spec S2/S3 : oreilles +0,09 T au-dessus du crane"),
]
CIBLES_TRAITS = [
    ("entraxe_yeux_sur_LT", "Entraxe des yeux / largeur de tete", 0.34, "spec S2 : 0,34 LT"),
    ("hauteur_oeil_sur_LT", "Hauteur d'oeil / largeur de tete", 0.14, "spec S2 : h ~ 0,14 LT"),
    ("ratio_oeil", "Ratio hauteur/largeur de l'oeil", 1.6, "spec S2 : rapport h/l ~ 1,6"),
    ("yeux_sous_crane_sur_T", "Centre des yeux sous le crane / hauteur de tete", 0.44, "spec S2 : yeux a 0,44 T sous le sommet du crane"),
    ("longueur_sourcil_sur_LT", "Longueur de sourcil / largeur de tete", 100.0 / 937.0, "spec S2 : sourcils ~100 px sur LT 937 px"),
    ("largeur_bouche_sur_LT", "Largeur de bouche / largeur de tete (INDICATIF)", 0.40, "spec S2 : 0,40 LT -- detection auto non fiable, hors verdict"),
]
SEUIL_PROP = 3.0     # %
SEUIL_TRAITS = 2.0   # %
SEUIL_DELTAE = 5.0   # DeltaE76 mediane vs orange median de charte (provisoire)
CHARTE = {"lumiere": (0xFC, 0x8B, 0x32), "median": (0xC9, 0x5D, 0x1D), "ombre": (0x8D, 0x2E, 0x0F)}


def ecart_pct(mesure, cible):
    if mesure is None or cible == 0:
        return None
    return 100.0 * (mesure - cible) / cible


def verdict_mesure(mesure, cible, seuil):
    e = ecart_pct(mesure, cible)
    if e is None:
        return {"mesure": None, "cible": cible, "ecart_pct": None, "verdict": "NON MESURABLE"}
    return {"mesure": round(float(mesure), 4), "cible": round(float(cible), 4),
            "ecart_pct": round(float(e), 2),
            "verdict": "PASS" if abs(e) <= seuil else "FAIL"}


def srgb_to_lab(rgb):
    def lin(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(rgb[0]), lin(rgb[1]), lin(rgb[2]))
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 1.00000
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    def f(t):
        return t ** (1.0 / 3.0) if t > 0.008856 else (7.787 * t + 16.0 / 116.0)
    fx, fy, fz = f(x), f(y), f(z)
    return (116.0 * fy - 16.0, 500.0 * (fx - fy), 200.0 * (fy - fz))


def delta_e(rgb1, rgb2):
    l1 = srgb_to_lab(rgb1)
    l2 = srgb_to_lab(rgb2)
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(l1, l2)))


def fail(msg):
    R["statut"] = "ECHEC"
    R["erreur"] = msg
    with open(os.path.join(OUTDIR, "mesures-porte.json"), "w", encoding="utf-8") as f:
        json.dump(R, f, indent=2, ensure_ascii=False)
    with open(os.path.join(OUTDIR, "ERREUR.txt"), "w", encoding="utf-8") as f:
        f.write(msg)
    raise RuntimeError(msg)


try:
    # ------------------------------------------------ 1. import
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if not os.path.exists(SRC):
        fail("GLB source introuvable : " + SRC)
    bpy.ops.import_scene.gltf(filepath=SRC)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    for o in [o for o in bpy.context.scene.objects if o.type != "MESH"]:
        bpy.data.objects.remove(o, do_unlink=True)
    if not meshes:
        fail("Aucun mesh apres import GLB")
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    mesh = bpy.context.view_layer.objects.active
    mesh.name = "CandidatPorte"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    verts = np.empty(len(mesh.data.vertices) * 3, dtype=np.float64)
    mesh.data.vertices.foreach_get("co", verts)
    verts = verts.reshape(-1, 3)
    vmin, vmax = verts.min(axis=0), verts.max(axis=0)
    z0 = float(vmin[2])
    H = float(vmax[2] - vmin[2])
    xc = float((vmin[0] + vmax[0]) / 2.0)
    yc = float((vmin[1] + vmax[1]) / 2.0)
    R["modele"] = {"sommets": int(len(verts)),
                   "triangles": int(sum(len(p.vertices) - 2 for p in mesh.data.polygons)),
                   "hauteur": round(H, 4), "largeur": round(float(vmax[0] - vmin[0]), 4),
                   "profondeur": round(float(vmax[1] - vmin[1]), 4)}
    log("Modele : H=%.3f, %d sommets" % (H, len(verts)))

    # ------------------------------------------------ 2. sens du visage
    band = verts[(verts[:, 2] > z0 + 0.55 * H) & (verts[:, 2] < z0 + 0.85 * H)]
    prot_plus = float(band[:, 1].max() - yc) if len(band) else 0.0
    prot_moins = float(yc - band[:, 1].min()) if len(band) else 0.0
    facing = 1.0 if prot_plus >= prot_moins else -1.0
    R["visage"] = {"direction_y": facing,
                   "methode": "protrusion max dans la bande 0,55H-0,85H vs centre Y (comme le test d'armature)"}
    log("Visage vers %sY" % ("+" if facing > 0 else "-"))

    # ------------------------------------------------ 3. profil de largeur
    NB = 256
    idx = np.clip(((verts[:, 2] - z0) / H * NB).astype(int), 0, NB - 1)
    largeur = np.zeros(NB)
    for b in range(NB):
        sel = verts[idx == b]
        if len(sel):
            largeur[b] = sel[:, 0].max() - sel[:, 0].min()
    # lissage (moyenne mobile 5) pour la recherche de pincement
    larg_s = np.convolve(largeur, np.ones(5) / 5.0, mode="same")

    def frac(z):
        return (z - z0) / H

    # Crane : sommet parmi les sommets centraux (exclut les oreilles, laterales)
    tete_approx = float(largeur[int(0.80 * NB):].max()) if largeur[int(0.80 * NB):].max() > 0 else float(largeur.max())
    centraux = verts[np.abs(verts[:, 0] - xc) <= 0.18 * tete_approx]
    crane_z = float(centraux[:, 2].max()) if len(centraux) else float(vmax[2])
    oreilles_z = float(vmax[2])

    # Pincement du cou : minimum local de largeur dans la zone attendue du menton
    lo, hi = int(0.40 * NB), int(0.72 * NB)
    seg = larg_s[lo:hi]
    b_pinch = lo + int(np.argmin(seg))
    z_pinch = z0 + (b_pinch + 0.5) / NB * H
    larg_pinch = float(larg_s[b_pinch])
    # largeur de tete : max au-dessus du pincement ; torse : max en dessous (hors jambes)
    larg_tete = float(larg_s[b_pinch:].max())
    larg_torse = float(larg_s[int(0.30 * NB):b_pinch].max()) if b_pinch > int(0.30 * NB) else float(larg_s[:b_pinch].max())
    pincement_net = larg_pinch < 0.85 * min(larg_tete, larg_torse)
    T_mes = crane_z - z_pinch
    R["geometrie"] = {
        "hauteur_totale_H": round(H, 4),
        "sommet_oreilles_z_frac": round(frac(oreilles_z), 4),
        "sommet_crane_z_frac": round(frac(crane_z), 4),
        "pincement": {"z_frac": round(frac(z_pinch), 4), "largeur": round(larg_pinch, 4),
                      "net": bool(pincement_net),
                      "note": "net = largeur au pincement < 85 % du min(tete, torse) ; sinon estimation faible (argmin de zone)"},
        "largeur_tete": round(larg_tete, 4),
        "largeur_max": round(float(largeur.max()), 4),
        "hauteur_tete_T_estimee": round(float(T_mes), 4),
    }
    log("Pincement z=%.3fH largeur=%.3f net=%s ; T=%.3f" % (frac(z_pinch), larg_pinch, pincement_net, T_mes))

    mesures_prop = {
        "tete_sur_H": T_mes / H,
        "largeur_tete_sur_H": larg_tete / H,
        "largeur_tete_sur_T": (larg_tete / T_mes) if T_mes > 0 else None,
        "pincement_sur_largeur_tete": (larg_pinch / larg_tete) if larg_tete > 0 else None,
        "menton_sur_H": frac(z_pinch),
        "envergure_sur_H": float(largeur.max()) / H,
        "oreilles_au_dessus_crane_sur_T": ((oreilles_z - crane_z) / T_mes) if T_mes > 0 else None,
    }

    # ------------------------------------------------ 4. rendus orthographiques
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    sh = scene.display.shading
    sh.light = "STUDIO"
    sh.color_type = "TEXTURE"
    sh.show_cavity = True
    scene.render.resolution_x = 900
    scene.render.resolution_y = 1260
    scene.render.film_transparent = True  # silhouette par le canal alpha (le fond Workbench n'est pas blanc pur)
    if scene.world is None:
        scene.world = bpy.data.worlds.new("World")
    scene.world.color = (1.0, 1.0, 1.0)
    cam_data = bpy.data.cameras.new("CamPorte")
    cam = bpy.data.objects.new("CamPorte", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = H * 1.30
    from mathutils import Vector
    centre = Vector((xc, yc, z0 + 0.50 * H))

    def rendre(nom, direction):
        d = Vector(direction)
        cam.location = centre + d * (H * 3.0)
        look = centre - cam.location
        cam.rotation_euler = look.to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = os.path.join(OUTDIR, nom + ".png")
        bpy.ops.render.render(write_still=True)
        log("Rendu : " + nom)

    face_dir = (0, facing, 0)    # camera du cote du visage (meme signe que la direction du visage)
    dos_dir = (0, -facing, 0)
    profil_dir = (1, 0, 0)       # vue de cote (profil)
    rendre("rendu-face", face_dir)
    rendre("rendu-profil", profil_dir)
    rendre("rendu-dos", dos_dir)

    # ------------------------------------------------ 5. analyse d'image (face)
    def charger_pixels(nom):
        img = bpy.data.images.load(os.path.join(OUTDIR, nom + ".png"))
        w, h = img.size
        px = np.empty(w * h * 4, dtype=np.float32)
        img.pixels.foreach_get(px)
        px = px.reshape(h, w, 4)  # ligne 0 = bas de l'image
        bpy.data.images.remove(img)
        return px

    img = charger_pixels("rendu-face")
    lum = img[:, :, :3].mean(axis=2)
    silh = img[:, :, 3] > 0.5  # silhouette par l'alpha (fond transparent)
    rows = np.where(silh.any(axis=1))[0]
    cols = np.where(silh.any(axis=0))[0]
    traits = {}
    fiabilite = {}
    if len(rows) and len(cols):
        r0, r1 = rows.min(), rows.max()
        h_px = float(r1 - r0 + 1)
        # largeur de tete sur le rendu, dans la zone au-dessus du pincement geometrique
        pinch_row = r0 + frac(z_pinch) * h_px
        tete_rows = silh[int(pinch_row):, :]
        larg_tete_px = float(np.max(tete_rows.sum(axis=1))) if tete_rows.any() else 0.0

        # encoche entre les jambes : colonne centrale, fond enferme sous la silhouette
        jambes_frac = None
        c_mid = silh[:, max(0, int(cols.mean()) - 6):int(cols.mean()) + 7]
        col_silh = c_mid.any(axis=1)
        # premier rang de silhouette en montant depuis le bas, par colonne centrale :
        # l'encoche = le plus haut "trou" de fond entre les deux pieds
        trou = (~col_silh) & (np.arange(len(col_silh)) > r0 + 2) & (np.arange(len(col_silh)) < r0 + 0.45 * h_px)
        if trou.any():
            jambes_frac = float((np.where(trou)[0].max() - r0) / h_px)
        mesures_prop["jambes_sur_H"] = jambes_frac
        fiabilite["jambes_sur_H"] = "rendu (encoche inter-jambes)" if jambes_frac else "non mesurable"

        # blobs sombres (yeux, sourcils, bouche) dans la zone du visage
        sombre = (lum < 0.22) & silh
        # sous-echantillonnage x3 pour l'etiquetage
        pas = 3
        grille = sombre[::pas, ::pas]
        gh, gw = grille.shape
        etiquettes = np.zeros((gh, gw), dtype=np.int32)
        comps = []
        courant = 0
        for gy in range(gh):
            for gx in range(gw):
                if grille[gy, gx] and etiquettes[gy, gx] == 0:
                    courant += 1
                    pile = [(gy, gx)]
                    etiquettes[gy, gx] = courant
                    pts = []
                    while pile:
                        y, x = pile.pop()
                        pts.append((y, x))
                        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < gh and 0 <= nx < gw and grille[ny, nx] and etiquettes[ny, nx] == 0:
                                etiquettes[ny, nx] = courant
                                pile.append((ny, nx))
                    comps.append(pts)
        # composants en coordonnees image pleine resolution
        infos = []
        for pts in comps:
            ys = np.array([p[0] for p in pts]) * pas
            xs = np.array([p[1] for p in pts]) * pas
            infos.append({"n": len(pts) * pas * pas, "cx": float(xs.mean()), "cy": float(ys.mean()),
                          "w": float(xs.max() - xs.min() + pas), "h": float(ys.max() - ys.min() + pas),
                          "ymin": float(ys.min()), "ymax": float(ys.max())})
        # zone visage : entre le pincement (menton) et le sommet du crane (geometrie)
        crane_row_pre = r0 + frac(crane_z) * h_px
        visage = [c for c in infos if pinch_row - 2 <= c["cy"] <= crane_row_pre + 2 and c["n"] >= 60]
        visage.sort(key=lambda c: -c["n"])
        yeux = []
        if len(visage) >= 2:
            # les deux plus gros composants de taille comparable = les yeux
            cand = sorted(visage[:4], key=lambda c: c["cx"])
            # choisir la paire la plus symetrique en taille et en hauteur
            meilleure = None
            for i in range(len(cand)):
                for j in range(i + 1, len(cand)):
                    a, b = cand[i], cand[j]
                    score = abs(a["h"] - b["h"]) / max(a["h"], b["h"]) + abs(a["cy"] - b["cy"]) / h_px
                    if meilleure is None or score < meilleure[0]:
                        meilleure = (score, a, b)
            if meilleure:
                yeux = [meilleure[1], meilleure[2]]
        if len(yeux) == 2 and larg_tete_px > 0:
            a, b = yeux
            entraxe = abs(b["cx"] - a["cx"])
            h_oeil = (a["h"] + b["h"]) / 2.0
            l_oeil = (a["w"] + b["w"]) / 2.0
            cy_yeux = (a["cy"] + b["cy"]) / 2.0
            crane_row = r1  # haut de silhouette ~ sommet des oreilles ; correction crane ci-dessous
            # sommet du crane sur le rendu : haut de la silhouette dans la bande centrale
            bande = silh[:, int(cols.min() + 0.35 * (cols.max() - cols.min())):int(cols.min() + 0.65 * (cols.max() - cols.min()))]
            lignes_bande = np.where(bande.any(axis=1))[0]
            if len(lignes_bande):
                crane_row = float(lignes_bande.max())
            T_px = (crane_row - pinch_row) if (crane_row - pinch_row) > 0 else h_px * (T_mes / H)
            traits["entraxe_yeux_sur_LT"] = entraxe / larg_tete_px
            traits["hauteur_oeil_sur_LT"] = h_oeil / larg_tete_px
            traits["ratio_oeil"] = (h_oeil / l_oeil) if l_oeil > 0 else None
            traits["yeux_sous_crane_sur_T"] = ((crane_row - cy_yeux) / T_px) if T_px > 0 else None
            fiabilite["traits_yeux"] = "rendu face, blobs sombres (methode validee sur la reference au test Pixal3D)"
            # sourcils : composants sombres fins au-dessus des yeux
            sourcils = [c for c in visage if c not in yeux and c["cy"] > cy_yeux + 0.03 * h_px
                        and c["w"] > c["h"] * 1.5 and c["n"] >= 60]
            if sourcils:
                traits["longueur_sourcil_sur_LT"] = float(np.mean([c["w"] for c in sourcils])) / larg_tete_px
                fiabilite["sourcils"] = "rendu face, composants fins au-dessus des yeux"
            # bouche : zone sous les yeux, composant sombre large et fin -> INDICATIF
            bouche = [c for c in visage if c not in yeux and c["cy"] < cy_yeux - 0.05 * h_px
                      and c["cy"] > pinch_row and c["w"] > c["h"] * 2.0]
            if bouche:
                traits["largeur_bouche_sur_LT"] = float(max(c["w"] for c in bouche)) / larg_tete_px
                fiabilite["bouche"] = "INDICATIF -- detection auto non fiable (invalidee sur la reference au test Pixal3D), hors verdict"
        else:
            fiabilite["traits_yeux"] = "yeux non detectes sur le rendu de face"
        R["rendu_face"] = {"silhouette_px": [int(h_px), int(cols.max() - cols.min() + 1)],
                           "largeur_tete_px": larg_tete_px,
                           "composants_sombres_visage": len(visage)}
    else:
        fiabilite["rendu"] = "silhouette introuvable sur le rendu de face"

    # museau (informatif, geometrie) : protrusion avant dans la bande des yeux
    if traits.get("yeux_sous_crane_sur_T") is not None and T_mes > 0:
        z_yeux = crane_z - traits["yeux_sous_crane_sur_T"] * T_mes
    else:
        z_yeux = z0 + 0.79 * H
    bande_m = verts[(verts[:, 2] > z_yeux - 0.30 * T_mes) & (verts[:, 2] < z_yeux + 0.05 * T_mes)] if T_mes > 0 else verts
    if len(bande_m):
        avant = float((bande_m[:, 1] * facing).max())
        arriere_tete = float((verts[verts[:, 2] > z_pinch][:, 1] * facing).min()) if (verts[:, 2] > z_pinch).any() else yc
        profondeur_tete = float((verts[verts[:, 2] > z_pinch][:, 1] * facing).max() - arriere_tete)
        R["museau_informatif"] = {
            "protrusion_avant_bande_museau": round(avant - yc * facing, 4),
            "profondeur_tete_estimee": round(profondeur_tete, 4),
            "note": "mesure brute informative : la spec ne fige aucune profondeur cible du museau (porte no 1 : 'plutot profond', sans chiffre). Aucun verdict.",
        }

    # ------------------------------------------------ 6. couleurs (texture)
    couleurs = {}
    img_tex = None
    for mat in bpy.data.materials:
        if not mat.use_nodes:
            continue
        for node in mat.node_tree.nodes:
            if node.type == "TEX_IMAGE" and node.image is not None:
                if img_tex is None or (node.image.size[0] * node.image.size[1] > img_tex.size[0] * img_tex.size[1]):
                    img_tex = node.image
    if img_tex is not None:
        w, h = img_tex.size
        px = np.empty(w * h * 4, dtype=np.float32)
        img_tex.pixels.foreach_get(px)
        px = px.reshape(-1, 4)[:, :3]
        pas = max(1, len(px) // 200000)
        echant = px[::pas]
        # restreindre aux texels "orange" (exclut yeux/fond eventuels de la texture)
        lum_e = echant.mean(axis=1)
        masque = (echant[:, 0] > 0.25) & (lum_e > 0.08) & (lum_e < 0.98)
        sel = echant[masque] if masque.any() else echant
        med = np.median(sel, axis=0)
        med_rgb = tuple(int(round(float(c) * 255)) for c in med)
        couleurs["texture"] = img_tex.name
        couleurs["mediane_rgb"] = med_rgb
        couleurs["mediane_hex"] = "#%02X%02X%02X" % med_rgb
        couleurs["deltaE_vs_charte"] = {
            k: round(delta_e(med_rgb, v), 2) for k, v in CHARTE.items()
        }
        couleurs["verdict"] = "PASS" if couleurs["deltaE_vs_charte"]["median"] <= SEUIL_DELTAE else "FAIL"
        couleurs["seuil_deltaE"] = SEUIL_DELTAE
        log("Couleurs : mediane %s, DeltaE vs median charte = %.2f" % (couleurs["mediane_hex"], couleurs["deltaE_vs_charte"]["median"]))
    else:
        couleurs["verdict"] = "NON MESURABLE"
        couleurs["note"] = "aucune texture image trouvee dans les materiaux"
    R["couleurs"] = couleurs

    # ------------------------------------------------ 7. verdicts
    R["proportions"] = {}
    for cle, libelle, cible, source in CIBLES_PROP:
        m = mesures_prop.get(cle)
        d = verdict_mesure(m, cible, SEUIL_PROP)
        d["libelle"] = libelle
        d["source_cible"] = source
        if cle in ("pincement_sur_largeur_tete", "tete_sur_H", "menton_sur_H", "largeur_tete_sur_T") and not pincement_net:
            d["fiabilite"] = "FAIBLE -- aucun pincement de cou net detecte : le menton est estime a l'argmin de zone"
        R["proportions"][cle] = d
    R["traits"] = {}
    for cle, libelle, cible, source in CIBLES_TRAITS:
        m = traits.get(cle)
        if "INDICATIF" in libelle:
            e = ecart_pct(m, cible)
            R["traits"][cle] = {"mesure": (round(float(m), 4) if m is not None else None),
                                "cible": cible, "ecart_pct": (round(float(e), 2) if e is not None else None),
                                "verdict": "INDICATIF (hors verdict)", "libelle": libelle, "source_cible": source}
        else:
            d = verdict_mesure(m, cible, SEUIL_TRAITS)
            d["libelle"] = libelle
            d["source_cible"] = source
            R["traits"][cle] = d
    R["fiabilite"] = fiabilite
    R["seuils"] = {"proportions_pct": SEUIL_PROP, "traits_pct": SEUIL_TRAITS, "deltaE_mediane": SEUIL_DELTAE}

    verdicts = [d["verdict"] for d in R["proportions"].values()] + \
               [d["verdict"] for d in R["traits"].values() if d["verdict"] in ("PASS", "FAIL", "NON MESURABLE")] + \
               [couleurs.get("verdict", "NON MESURABLE")]
    R["verdict_global"] = "PASS" if all(v == "PASS" for v in verdicts) else "FAIL"
    R["statut"] = "TERMINE"
    with open(os.path.join(OUTDIR, "mesures-porte.json"), "w", encoding="utf-8") as f:
        json.dump(R, f, indent=2, ensure_ascii=False)
    with open(os.path.join(OUTDIR, "FIN.txt"), "w", encoding="utf-8") as f:
        f.write("PASS-GABARIT\nverdict_global_modele=%s\n" % R["verdict_global"])
    log("TERMINE -- verdict global du modele : " + R["verdict_global"])

except Exception:
    tb = traceback.format_exc()
    print(tb, flush=True)
    try:
        R.setdefault("statut", "ECHEC")
        R["traceback"] = tb
        with open(os.path.join(OUTDIR, "mesures-porte.json"), "w", encoding="utf-8") as f:
            json.dump(R, f, indent=2, ensure_ascii=False)
        with open(os.path.join(OUTDIR, "ERREUR.txt"), "w", encoding="utf-8") as f:
            f.write(tb)
    except Exception:
        pass
