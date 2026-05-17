from controller import Robot
robot = Robot()
timestep = int(robot.getBasicTimeStep())

# Moteurs
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



ds0 = robot.getDevice("ds0")
ds1 = robot.getDevice("ds1")
ds2 = robot.getDevice("ds2")
ds3 = robot.getDevice("ds3")
ds4 = robot.getDevice("ds4")

for ds in [ds0, ds1, ds2, ds3, ds4]:
    ds.enable(timestep)
robot.step(timestep)
    
    

s_base   = robot.getDevice("base_sensor")
s_upper  = robot.getDevice("upperarm_sensor")
s_fore   = robot.getDevice("forearm_sensor")
s_wrist  = robot.getDevice("wrist_sensor")
s_rot    = robot.getDevice("rotational_wrist_sensor")
s_grip_l = robot.getDevice("gripper::left_sensor")
s_grip_r = robot.getDevice("gripper::right_sensor")

for s in [s_base, s_upper, s_fore, s_wrist, s_rot, s_grip_l, s_grip_r]:
    s.enable(timestep)

receiver = robot.getDevice("receiver")
receiver.enable(timestep)
receiver.setChannel(1)

emitter = robot.getDevice("emitter")
emitter.setChannel(0)

#--------------------------------------------------------------- 
def attendre(steps):
    for _ in range(steps):
        robot.step(timestep)
        afficher_capteurs()
        
def attendre_pos(sensor, target, tolerance=0.01):
    while robot.step(timestep) != -1:
        afficher_capteurs()
        if abs(sensor.getValue() - target) < tolerance:
            break  
def afficher_capteurs():
    print(f"base={s_base.getValue():.3f} | "
          f"upper={s_upper.getValue():.3f} | "
          f"fore={s_fore.getValue():.3f} | "
          f"wrist={s_wrist.getValue():.3f} | "
          f"grip_L={s_grip_l.getValue():.3f} | "
          f"grip_R={s_grip_r.getValue():.3f} | "
          f"ds0={ds0.getValue():.1f} | ")
          
#---------------------------------------------------------------   
def pos_can():
    base.setPosition(3.015)
    upperarm.setPosition(-0.25)
    forearm.setPosition(1.45)
    wrist.setPosition(0)
    rotational_wrist.setPosition(-2.9932)
    gripper_left.setPosition(-1.22)
    gripper_right.setPosition(1.22)
    attendre(50)

def bouger_soda():
    gripper_left.setPosition(-0.02)
    gripper_right.setPosition(0.02)
    attendre(80)
    upperarm.setPosition(-0.4)
    attendre_pos(s_upper, -0.4)
    base.setPosition(2.103)
    attendre_pos(s_base, 2.103)
    gripper_left.setPosition(-1.22)
    gripper_right.setPosition(1.22)
    attendre(50)
    print("ARM : objet déposé !")
 #---------------------------------------------------------------
def pos_Bouteille():
    base.setPosition(3.015)
    upperarm.setPosition(-0.18)
    forearm.setPosition(1.25)
    wrist.setPosition(0)
    rotational_wrist.setPosition(-2.9932)
    gripper_left.setPosition(-1.22)
    gripper_right.setPosition(1.22)
    attendre(50)
    
def bouger_Bouteille():
    gripper_left.setPosition(-0.3)
    gripper_right.setPosition(0.3)
    attendre(80)
    upperarm.setPosition(-0.22)
    attendre_pos(s_upper, -0.22)
    base.setPosition(3.927)
    attendre_pos(s_base, 3.927)
    gripper_left.setPosition(-1)
    gripper_right.setPosition(1)
    attendre(70)
    print("ARM : objet déposé !")
#---------------------------------------------------------------  
def pos_initial():
            base.setPosition(3.015)
            upperarm.setPosition(-0.20)
            forearm.setPosition(1.25)
            wrist.setPosition(0)
            rotational_wrist.setPosition(-2.9932)
            gripper_left.setPosition(-1.22)
            gripper_right.setPosition(1.22)

step = 0
msg_recu = None  # stocke le message reçu
en_cours = False 
pos_initial()

while robot.step(timestep) != -1:
    step += 1

    if step % 10 == 0:
         afficher_capteurs()   
              
    # stocke le message dès qu'il arrive
    if receiver.getQueueLength() > 0:
        msg = receiver.getString()
        receiver.nextPacket()
        if msg in ["WATER", "SODA"]:
            msg_recu = msg
            print(f"ARM : message vision reçu → {msg_recu}, position {msg_recu}")
            
    if not en_cours:
        if msg_recu == "SODA":
            pos_can()
        elif msg_recu == "WATER":
            pos_Bouteille()

    # déclenche quand ds0 détecte ET qu'on a un message
    
            # --- SÉQUENCE DE SAISIE ET DE TRI ---
    if msg_recu is not None and ds0.getValue() > 10 and not en_cours:
        en_cours = True
        print(f"ARM : DÉCLENCHEMENT → {msg_recu}  ds0={ds0.getValue():.1f}")
        if msg_recu == "SODA":
            bouger_soda()
        elif msg_recu == "WATER":
            bouger_Bouteille()
                # Note : j'ai remis la plongée pour l'eau aussi pour que ça marche pareil



    
            # --- RETOUR IDLE ---
        pos_initial()
        attendre(20)
 
        msg_recu = None
        en_cours = False
            # --- FIN DE CYCLE ---
        emitter.send("DONE".encode())
        print("ARM : DONE — retour position initial")