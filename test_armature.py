# Test d'armature jetable sur le brouillon Pixal3D SV -- Blender headless (Fractal)
# Voie 3D, etape 1 du PLAN-VOIE-3D-V1. Brouillon jetable uniquement, jamais le modele reel.
# Pose une armature humanoide normalisee (noms VRM + chaines prefixees onyx_),
# skinning automatique, tests de deformation de base, rendus temoins, mesures JSON.
import bpy
import json
import math
import os
import traceback
from mathutils import Vector

SRC = r"C:\Users\<utilisateur>\ComfyUI\output\3d\pixal3d_sv_onyx_00001.glb"
OUTDIR = r"C:\Users\<utilisateur>\onyx-3d\armature-test-2026-11-22"
RESULTS = {}

os.makedirs(OUTDIR, exist_ok=True)


def log(msg):
    print("[ARMATURE-TEST] " + str(msg), flush=True)


def fail(msg):
    RESULTS["statut"] = "ECHEC"
    RESULTS["erreur"] = msg
    with open(os.path.join(OUTDIR, "mesures.json"), "w", encoding="utf-8") as f:
        json.dump(RESULTS, f, indent=2, ensure_ascii=False)
    with open(os.path.join(OUTDIR, "ERREUR.txt"), "w", encoding="utf-8") as f:
        f.write(msg)
    raise RuntimeError(msg)


try:
    # ---------- 1. Scene propre + import ----------
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if not os.path.exists(SRC):
        fail("GLB source introuvable : " + SRC)
    bpy.ops.import_scene.gltf(filepath=SRC)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    others = [o for o in bpy.context.scene.objects if o.type != "MESH"]
    for o in others:
        bpy.data.objects.remove(o, do_unlink=True)
    if not meshes:
        fail("Aucun mesh apres import GLB")
    log("Objets mesh importes : %d" % len(meshes))

    # Joindre en un seul mesh si besoin
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    mesh = bpy.context.view_layer.objects.active
    mesh.name = "BrouillonSV"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # ---------- 2. Mesures du brouillon ----------
    import numpy as np
    verts = np.empty(len(mesh.data.vertices) * 3, dtype=np.float64)
    mesh.data.vertices.foreach_get("co", verts)
    verts = verts.reshape(-1, 3)
    vmin = verts.min(axis=0)
    vmax = verts.max(axis=0)
    z0 = float(vmin[2])
    H = float(vmax[2] - vmin[2])
    W = float(vmax[0] - vmin[0])
    D = float(vmax[1] - vmin[1])
    yc = float((vmin[1] + vmax[1]) / 2.0)
    xc = float((vmin[0] + vmax[0]) / 2.0)
    RESULTS["brouillon"] = {
        "fichier": SRC,
        "sommets": int(len(mesh.data.vertices)),
        "triangles": int(sum(len(p.vertices) - 2 for p in mesh.data.polygons)),
        "hauteur": round(H, 4),
        "largeur": round(W, 4),
        "profondeur": round(D, 4),
    }
    log("Brouillon : H=%.3f L=%.3f P=%.3f, %d sommets" % (H, W, D, len(mesh.data.vertices)))

    # ---------- 3. Detection du sens du visage (heuristique de protrusion) ----------
    # Bandes de hauteur 0.55H..0.85H (zone museau) : la face est du cote ou le mesh
    # depasse le plus le centre en Y.
    band = verts[(verts[:, 2] > z0 + 0.55 * H) & (verts[:, 2] < z0 + 0.85 * H)]
    if len(band):
        prot_plus = float(band[:, 1].max() - yc)
        prot_moins = float(yc - band[:, 1].min())
    else:
        prot_plus = prot_moins = 0.0
    facing = 1.0 if prot_plus >= prot_moins else -1.0  # +1 = visage vers +Y
    RESULTS["visage"] = {
        "direction_y": facing,
        "protrusion_plus_y": round(prot_plus, 4),
        "protrusion_moins_y": round(prot_moins, 4),
        "methode": "protrusion max du museau dans la bande 0.55H-0.85H, comparee au centre Y",
    }
    log("Visage detecte vers %sY" % ("+" if facing > 0 else "-"))

    def Z(frac):
        return z0 + frac * H

    def P(x_frac, z_frac, y_off=0.0):
        return Vector((xc + x_frac * H, yc + y_off, Z(z_frac)))

    # ---------- 4. Armature normalisee (noms VRM + chaines onyx_) ----------
    arm_data = bpy.data.armatures.new("ArmatureSocleTest")
    arm = bpy.data.objects.new("ArmatureSocleTest", arm_data)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")

    # (nom, tete, queue, parent, connecte)
    B = []
    B.append(("hips",        P(0, 0.235),      P(0, 0.315),      None, False))
    B.append(("spine",       P(0, 0.315),      P(0, 0.395),      "hips", True))
    B.append(("chest",       P(0, 0.395),      P(0, 0.465),      "spine", True))
    B.append(("upperChest",  P(0, 0.465),      P(0, 0.515),      "chest", True))
    B.append(("neck",        P(0, 0.515),      P(0, 0.555),      "upperChest", True))
    B.append(("head",        P(0, 0.555),      P(0, 0.820),      "neck", True))
    B.append(("onyx_ear.L",  P(0.100, 0.900),  P(0.170, 1.000),  "head", False))
    B.append(("onyx_ear.R",  P(-0.100, 0.900), P(-0.170, 1.000), "head", False))
    for side, s in (("left", 1.0), ("right", -1.0)):
        B.append((side + "Shoulder",  P(s * 0.030, 0.485), P(s * 0.120, 0.475), "upperChest", False))
        B.append((side + "UpperArm",  P(s * 0.120, 0.475), P(s * 0.185, 0.355), side + "Shoulder", True))
        B.append((side + "LowerArm",  P(s * 0.185, 0.355), P(s * 0.215, 0.255), side + "UpperArm", True))
        B.append((side + "Hand",      P(s * 0.215, 0.255), P(s * 0.230, 0.195), side + "LowerArm", True))
        B.append((side + "UpperLeg",  P(s * 0.062, 0.260), P(s * 0.068, 0.135), "hips", False))
        B.append((side + "LowerLeg",  P(s * 0.068, 0.135), P(s * 0.068, 0.055), side + "UpperLeg", True))
        B.append((side + "Foot",      P(s * 0.068, 0.055), P(s * 0.068, 0.012), side + "LowerLeg", True))
        B.append((side + "Toes",      P(s * 0.068, 0.012), P(s * 0.068, 0.012, facing * 0.070), side + "Foot", True))

    created = {}
    for name, head, tail, parent, conn in B:
        b = arm_data.edit_bones.new(name)
        b.head = head
        b.tail = tail
        created[name] = b
    for name, head, tail, parent, conn in B:
        if parent:
            created[name].parent = created[parent]
            created[name].use_connect = conn
    bone_names = [b[0] for b in B]
    RESULTS["armature"] = {"os": bone_names, "nombre_os": len(bone_names)}
    log("Armature creee : %d os" % len(bone_names))
    bpy.ops.object.mode_set(mode="OBJECT")

    # ---------- 5. Skinning (auto, replis documentes, succes MESURE) ----------
    # Lecon du 1er essai : parent_set(ARMATURE_AUTO) ne leve pas d'exception quand le
    # bone heat echoue -- il cree des groupes VIDES. Le succes se mesure donc :
    # fraction de sommets sans aucun poids apres chaque tentative.
    def nettoyer_skinning():
        for m in list(mesh.modifiers):
            if m.type == "ARMATURE":
                mesh.modifiers.remove(m)
        mesh.vertex_groups.clear()
        mesh.parent = None

    def mesurer_sans_poids():
        n = 0
        for v in mesh.data.vertices:
            s = 0.0
            for g in v.groups:
                s += g.weight
            if s <= 0.0:
                n += 1
        return n

    def tenter(mode):
        nettoyer_skinning()
        bpy.ops.object.select_all(action="DESELECT")
        mesh.select_set(True)
        arm.select_set(True)
        bpy.context.view_layer.objects.active = arm
        try:
            bpy.ops.object.parent_set(type=mode)
        except Exception as e:
            log("Tentative %s : exception %s" % (mode, e))
            return None
        if not any(m.type == "ARMATURE" for m in mesh.modifiers):
            log("Tentative %s : aucun modificateur armature" % mode)
            return None
        n = mesurer_sans_poids()
        frac = n / float(len(mesh.data.vertices))
        log("Tentative %s : %d sommets sans poids (%.2f %%)" % (mode, n, 100.0 * frac))
        return frac

    def retirer_os(noms):
        bpy.ops.object.select_all(action="DESELECT")
        arm.select_set(True)
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode="EDIT")
        for n in noms:
            if n in arm_data.edit_bones:
                arm_data.edit_bones.remove(arm_data.edit_bones[n])
        bpy.ops.object.mode_set(mode="OBJECT")

    tentatives = []
    methode = None
    seuil = 0.50  # succes = au plus 50 % de sommets sans poids

    f = tenter("ARMATURE_AUTO")
    tentatives.append({"mode": "ARMATURE_AUTO complet", "sans_poids_frac": f})
    if f is not None and f <= seuil:
        methode = "ARMATURE_AUTO (poids automatiques, bone heat)"

    if methode is None:
        retirer_os(("leftToes", "rightToes", "onyx_ear.L", "onyx_ear.R"))
        RESULTS["armature"]["repli_1"] = "orteils et oreilles retires pour la tentative auto reduite"
        f = tenter("ARMATURE_AUTO")
        tentatives.append({"mode": "ARMATURE_AUTO sans orteils ni oreilles", "sans_poids_frac": f})
        if f is not None and f <= seuil:
            methode = "ARMATURE_AUTO sans orteils ni oreilles (repli 1)"

    if methode is None:
        # Les enveloppes ne dependent pas de la diffusion de chaleur : elles
        # fonctionnent sur les meshes denses non manifoldes de type Pixal3D.
        bpy.ops.object.select_all(action="DESELECT")
        arm.select_set(True)
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode="EDIT")
        for b in arm_data.edit_bones:
            b.envelope_distance = 0.40 * H
        bpy.ops.object.mode_set(mode="OBJECT")
        f = tenter("ARMATURE_ENVELOPE")
        tentatives.append({"mode": "ARMATURE_ENVELOPE (distance 0.40H)", "sans_poids_frac": f})
        if f is not None and f <= seuil:
            methode = "ARMATURE_ENVELOPE (repli 2)"

    if methode is None:
        fail("Skinning impossible : toutes les tentatives ont laisse plus de 50 %% de sommets sans poids : " + json.dumps(tentatives))

    sans_poids = mesurer_sans_poids()
    RESULTS["skinning"] = {
        "methode": methode,
        "tentatives": tentatives,
        "groupes_sommets": len(mesh.vertex_groups),
        "sommets_sans_poids": int(sans_poids),
        "sommets_sans_poids_pct": round(100.0 * sans_poids / len(mesh.data.vertices), 3),
    }
    log("Skinning retenu : " + methode)

    # Sauvegarde du .blend au repos + export GLB au repos
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUTDIR, "armature-test.blend"))

    def positions_evaluees():
        deps = bpy.context.evaluated_depsgraph_get()
        ev = mesh.evaluated_get(deps)
        tmp = ev.to_mesh()
        arr = np.empty(len(tmp.vertices) * 3, dtype=np.float64)
        tmp.vertices.foreach_get("co", arr)
        ev.to_mesh_clear()
        return arr.reshape(-1, 3)

    rest = positions_evaluees()

    # ---------- 6. Rendu ----------
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    sh = scene.display.shading
    sh.light = "STUDIO"
    sh.color_type = "TEXTURE"
    sh.show_cavity = True
    scene.render.resolution_x = 700
    scene.render.resolution_y = 1000
    scene.render.film_transparent = False
    if scene.world is None:
        scene.world = bpy.data.worlds.new("World")
    scene.world.color = (0.85, 0.85, 0.85)

    cam_data = bpy.data.cameras.new("CamTemoin")
    cam = bpy.data.objects.new("CamTemoin", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = H * 1.30
    centre = Vector((xc, yc, Z(0.48)))

    def rendre(nom, direction):
        d = Vector(direction)
        cam.location = centre + d * (H * 3.0)
        quat = d.to_track_quat("Z", "Y") if abs(d.z) < 0.99 else d.to_track_quat("Z", "X")
        # camera regarde le long de -Z local : on vise le centre
        look = (centre - cam.location)
        cam.rotation_euler = look.to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = os.path.join(OUTDIR, nom + ".png")
        bpy.ops.render.render(write_still=True)
        log("Rendu : " + nom)

    vues = {
        "sud": (0, -1, 0),
        "nord": (0, 1, 0),
        "est": (1, 0, 0),
        "ouest": (-1, 0, 0),
    }
    face_view = "nord" if facing > 0 else "sud"
    for nom_vue, d in vues.items():
        rendre("neutre_" + nom_vue, d)

    # ---------- 7. Tests de deformation ----------
    def reset_pose():
        for pb in arm.pose.bones:
            pb.rotation_euler = (0.0, 0.0, 0.0)
            pb.location = (0.0, 0.0, 0.0)
            pb.scale = (1.0, 1.0, 1.0)
        bpy.context.view_layer.update()

    def mesurer(nom_pose):
        pos = positions_evaluees()
        delta = np.linalg.norm(pos - rest, axis=1)
        return {
            "pose": nom_pose,
            "deplacement_moyen": round(float(delta.mean()), 5),
            "deplacement_max": round(float(delta.max()), 5),
            "sommets_bouges_pct": round(100.0 * float((delta > 0.01 * H).sum()) / len(delta), 2),
        }

    tests = []
    deg = math.radians
    specs = [
        ("tete_inclinee", [("head", (0.0, 0.0, deg(20)))]),
        ("bras_leve", [("leftUpperArm", (deg(-65), 0.0, 0.0))]),
        ("tronc_penche", [("spine", (deg(12), 0.0, 0.0)), ("chest", (deg(8), 0.0, 0.0))]),
        ("jambe_pas", [("leftUpperLeg", (deg(-25), 0.0, 0.0)), ("leftLowerLeg", (deg(12), 0.0, 0.0))]),
    ]
    for nom_pose, rots in specs:
        reset_pose()
        for bone_name, rot in rots:
            if bone_name in arm.pose.bones:
                arm.pose.bones[bone_name].rotation_mode = "XYZ"
                arm.pose.bones[bone_name].rotation_euler = rot
        bpy.context.view_layer.update()
        m = mesurer(nom_pose)
        tests.append(m)
        log("Pose %s : max=%.4f moy=%.5f bouges=%.1f%%" % (nom_pose, m["deplacement_max"], m["deplacement_moyen"], m["sommets_bouges_pct"]))
        rendre("pose_" + nom_pose, vues[face_view])
    reset_pose()
    RESULTS["deformations"] = tests

    # ---------- 8. Export GLB du test (au repos) ----------
    bpy.ops.object.select_all(action="DESELECT")
    mesh.select_set(True)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = mesh
    glb_out = os.path.join(OUTDIR, "armature-test.glb")
    bpy.ops.export_scene.gltf(filepath=glb_out, export_format="GLB")
    RESULTS["export_glb"] = {"fichier": glb_out, "taille": os.path.getsize(glb_out)}
    log("Export GLB : %d octets" % RESULTS["export_glb"]["taille"])

    RESULTS["statut"] = "PASS"
    RESULTS["rendus"] = sorted(f for f in os.listdir(OUTDIR) if f.endswith(".png"))
    with open(os.path.join(OUTDIR, "mesures.json"), "w", encoding="utf-8") as f:
        json.dump(RESULTS, f, indent=2, ensure_ascii=False)
    with open(os.path.join(OUTDIR, "FIN.txt"), "w", encoding="utf-8") as f:
        f.write("PASS\n")
    log("TERMINE -- PASS")

except Exception:
    tb = traceback.format_exc()
    print(tb, flush=True)
    try:
        RESULTS.setdefault("statut", "ECHEC")
        RESULTS["traceback"] = tb
        with open(os.path.join(OUTDIR, "mesures.json"), "w", encoding="utf-8") as f:
            json.dump(RESULTS, f, indent=2, ensure_ascii=False)
        with open(os.path.join(OUTDIR, "ERREUR.txt"), "w", encoding="utf-8") as f:
            f.write(tb)
    except Exception:
        pass
