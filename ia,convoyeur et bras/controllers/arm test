from controller import Robot

robot = Robot()
timestep = int(robot.getBasicTimeStep())

# ── Moteurs ──────────────────────────────────────────────────────────────────
base             = robot.getDevice("base")
upperarm         = robot.getDevice("upperarm")
forearm          = robot.getDevice("forearm")
wrist            = robot.getDevice("wrist")
rotational_wrist = robot.getDevice("rotational_wrist")
gripper_left     = robot.getDevice("gripper::left")
gripper_right    = robot.getDevice("gripper::right")

gripper_left.setAvailableForce(200.0)
gripper_right.setAvailableForce(200.0)

for m in [base, upperarm, forearm, wrist, rotational_wrist, gripper_left, gripper_right]:
    m.setVelocity(0.5)

# ── Capteurs de distance ─────────────────────────────────────────────────────
ds0 = robot.getDevice("ds0")
ds1 = robot.getDevice("ds1")
ds2 = robot.getDevice("ds2")
ds3 = robot.getDevice("ds3")
ds4 = robot.getDevice("ds4")

for ds in [ds0, ds1, ds2, ds3, ds4]:
    ds.enable(timestep)
robot.step(timestep)

# ── Capteurs de position ─────────────────────────────────────────────────────
s_base   = robot.getDevice("base_sensor")
s_upper  = robot.getDevice("upperarm_sensor")
s_fore   = robot.getDevice("forearm_sensor")
s_wrist  = robot.getDevice("wrist_sensor")
s_rot    = robot.getDevice("rotational_wrist_sensor")
s_grip_l = robot.getDevice("gripper::left_sensor")
s_grip_r = robot.getDevice("gripper::right_sensor")

for s in [s_base, s_upper, s_fore, s_wrist, s_rot, s_grip_l, s_grip_r]:
    s.enable(timestep)

# ── Communication ─────────────────────────────────────────────────────────────
receiver = robot.getDevice("receiver")
receiver.enable(timestep)
receiver.setChannel(1)

emitter = robot.getDevice("emitter")
emitter.setChannel(0)


# ── Utilitaires ───────────────────────────────────────────────────────────────
def attendre(steps):
    for _ in range(steps):
        robot.step(timestep)


def aller_position_basse():
    """Position de repos / attente définie sur les images."""
    base.setPosition(0)
    upperarm.setPosition(-2.44)
    forearm.setPosition(4.21)
    wrist.setPosition(-4.05)
    rotational_wrist.setPosition(-5.8)
    gripper_left.setPosition(-1.22)
    gripper_right.setPosition(1.22)


def aller_idle():
    """Retour à la position idle après saisie."""
    base.setPosition(0)
    upperarm.setPosition(-0.20)
    forearm.setPosition(1.25)
    wrist.setPosition(0)
    rotational_wrist.setPosition(-2.9932)
    gripper_left.setPosition(-1.22)
    gripper_right.setPosition(1.22)


def saisir_soda():
    gripper_left.setPosition(-0.1)
    gripper_right.setPosition(0.1)
    attendre(40)
    upperarm.setPosition(-0.205)
    attendre(20)
    base.setPosition(5.8)
    attendre(50)
    gripper_left.setPosition(-1.22)
    gripper_right.setPosition(1.22)
    attendre(50)
    print("ARM : SODA déposé !")


def saisir_water():
    gripper_left.setPosition(-0.2)
    gripper_right.setPosition(0.2)
    attendre(80)
    upperarm.setPosition(-0.205)
    base.setPosition(0.85)
    attendre(100)
    gripper_left.setPosition(-1.22)
    gripper_right.setPosition(1.22)
    attendre(50)
    print("ARM : EAU déposée !")


# ── Position de départ ────────────────────────────────────────────────────────
aller_position_basse()

# ── Variables d'état ──────────────────────────────────────────────────────────
#
#   msg_vision  : dernier label envoyé par vision.py  ("WATER" | "SODA" | None)
#                 il est stocké dès réception et conservé jusqu'au déclenchement.
#
#   objet_proche: True dès que ds0 détecte un objet (seuil > 10).
#                 Séparé du message pour ne pas dépendre du timing.
#
msg_vision   = None   # ← reçu depuis vision.py via supervisor
objet_proche = False  # ← mis à True par ds0 indépendamment
en_cours     = False  # ← True pendant une séquence de saisie (anti-rebond)
step         = 0

while robot.step(timestep) != -1:
    step += 1

    # ── 1. Lecture du message de vision (indépendant de la proximité) ─────────
    #    On mémorise WATER ou SODA dès que vision.py le détecte.
    #    Le message reste en mémoire même si l'objet n'est pas encore près du bras.
    if receiver.getQueueLength() > 0:
        msg = receiver.getString()
        receiver.nextPacket()
        if msg in ["WATER", "SODA"]:
            msg_vision = msg
            print(f"ARM : message vision reçu → {msg_vision}")

    # ── 2. Lecture de la proximité (indépendant du message) ───────────────────
    #    ds0 dit si un objet est physiquement proche du bras.
    #    Ici on utilise un seuil > 10, adapte selon ta lookupTable.
    if ds0.getValue() > 10:
        objet_proche = True

    # ── 3. Log périodique ─────────────────────────────────────────────────────
    if step % 10 == 0:
        print(f"base={s_base.getValue():.3f} | "
              f"upper={s_upper.getValue():.3f} | "
              f"fore={s_fore.getValue():.3f} | "
              f"wrist={s_wrist.getValue():.3f} | "
              f"grip_L={s_grip_l.getValue():.3f} | "
              f"grip_R={s_grip_r.getValue():.3f} | "
              f"ds0={ds0.getValue():.1f} | "
              f"msg_vision={msg_vision} | "
              f"objet_proche={objet_proche}")

    # ── 4. Déclenchement : les deux conditions réunies, séquence non en cours ─
    #
    #    On déclenche SEULEMENT quand :
    #      - vision a identifié un objet  (msg_vision != None)
    #      - ET ds0 confirme la proximité (objet_proche == True)
    #      - ET on n'est pas déjà en train de saisir (en_cours == False)
    #
    if msg_vision is not None and objet_proche and not en_cours:
        en_cours = True
        print(f"ARM : DÉCLENCHEMENT → {msg_vision}  ds0={ds0.getValue():.1f}")

        if msg_vision == "SODA":
            saisir_soda()
        elif msg_vision == "WATER":
            saisir_water()

        # Retour position basse (celle des images) puis idle
        aller_idle()
        attendre(20)

        # Reset des deux flags indépendants
        msg_vision   = None
        objet_proche = False
        en_cours     = False

        emitter.send("DONE".encode())
        print("ARM : DONE — retour idle")