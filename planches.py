# -*- coding: utf-8 -*-
"""Planches temoins numerotees du test d'armature jetable (2026-11-22).
Compose, depuis les rendus Blender recuperes de Fractal :
  - planche-1-neutre-quatre-vues.png : le brouillon skine, 4 vues orthogonales
  - planche-2-poses.png              : neutre + 4 poses de deformation
Chaque panneau est numerote et legende. Fond blanc, texte fonce.
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

ICI = os.path.dirname(os.path.abspath(__file__))
MESURES = json.load(open(os.path.join(ICI, "mesures.json"), encoding="utf-8"))

PANEL_W = 500
LABEL_H = 64
GAP = 16
BG = (255, 255, 255)
FG = (30, 30, 30)


def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()


def panneau(fichier, titre, sous_titre):
    img = Image.open(os.path.join(ICI, fichier)).convert("RGB")
    ratio = PANEL_W / float(img.width)
    img = img.resize((PANEL_W, int(img.height * ratio)), Image.LANCZOS)
    panneau_img = Image.new("RGB", (PANEL_W, img.height + LABEL_H), BG)
    panneau_img.paste(img, (0, LABEL_H))
    d = ImageDraw.Draw(panneau_img)
    d.text((10, 8), titre, fill=FG, font=font(22))
    d.text((10, 36), sous_titre, fill=(90, 90, 90), font=font(17))
    return panneau_img


def planche(panneaux, sortie):
    cols = 2
    rows = (len(panneaux) + cols - 1) // cols
    h_max = max(p.height for p in panneaux)
    W = cols * PANEL_W + (cols + 1) * GAP
    H = rows * h_max + (rows + 1) * GAP
    toile = Image.new("RGB", (W, H), BG)
    for i, p in enumerate(panneaux):
        x = GAP + (i % cols) * (PANEL_W + GAP)
        y = GAP + (i // cols) * (h_max + GAP)
        toile.paste(p, (x, y))
    toile.save(os.path.join(ICI, sortie))
    print("OK", sortie, toile.size)


def main():
    vues = {}
    for nom, desc in (("neutre_sud", "vue sud (face)"), ("neutre_nord", "vue nord (dos)"),
                      ("neutre_est", "vue est (profil)"), ("neutre_ouest", "vue ouest (profil)")):
        vues[nom] = desc
    planche([
        panneau("neutre_sud.png", "1 - Neutre, vue sud", "face - visage detecte vers -Y"),
        panneau("neutre_nord.png", "2 - Neutre, vue nord", "dos"),
        panneau("neutre_est.png", "3 - Neutre, vue est", "profil"),
        panneau("neutre_ouest.png", "4 - Neutre, vue ouest", "profil"),
    ], "planche-1-neutre-quatre-vues.png")

    defs = {d["pose"]: d for d in MESURES.get("deformations", [])}

    def legende(cle, titre_pose):
        d = defs.get(cle, {})
        if not d:
            return titre_pose
        return "max %.3f - moy %.4f - %.1f %% bouges" % (
            d.get("deplacement_max", 0), d.get("deplacement_moyen", 0),
            d.get("sommets_bouges_pct", 0))

    planche([
        panneau("neutre_sud.png", "5 - Reference neutre (sud)", "avant poses"),
        panneau("pose_tete_inclinee.png", "6 - Tete inclinee 20 deg", legende("tete_inclinee", "tete + cou")),
        panneau("pose_bras_leve.png", "7 - Bras gauche leve -65 deg", legende("bras_leve", "epaule gauche")),
        panneau("pose_tronc_penche.png", "8 - Tronc penche 12+8 deg", legende("tronc_penche", "spine + chest")),
        panneau("pose_jambe_pas.png", "9 - Jambe droite, pas -25/+12 deg", legende("jambe_pas", "hanche + genou droits")),
    ], "planche-2-poses.png")


if __name__ == "__main__":
    main()
