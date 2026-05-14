from controller import Supervisor
import random

supervisor = Supervisor()
timestep = int(supervisor.getBasicTimeStep())

receiver = supervisor.getDevice("receiver")
receiver.enable(timestep)
receiver.setChannel(0)   # ← écoute TOUS les channels

emitter = supervisor.getDevice("emitter")
emitter.setChannel(1)    # envoie au bras sur channel 1

root = supervisor.getRoot()
children = root.getField("children")

SPAWN_POS = [-0.6, 0, 0.2]
current_obj_node = None

def spawn_object():
    global current_obj_node
    obj_type = random.choice(["WaterBottle", "Can"])
    node_str = f"""
    DEF TARGET Solid {{
      translation {SPAWN_POS[0]} {SPAWN_POS[1]} {SPAWN_POS[2]}
      children [ DEF ITEM {obj_type} {{ }} ]
      name "{obj_type}"
      boundingObject Box {{ size 0.08 0.2 0.08 }}
      physics Physics {{ mass 0.2 }}
    }}
    """
    children.importMFNodeFromString(-1, node_str)
    current_obj_node = supervisor.getFromDef("TARGET")
    print(f"SUPERVISOR : {obj_type} spawné")

spawn_object()

while supervisor.step(timestep) != -1:
    if receiver.getQueueLength() > 0:
        msg = receiver.getString()
        receiver.nextPacket()
        print(f"SUPERVISOR reçoit : {msg}")

        if msg in ["WATER", "SODA"]:
            emitter.send(msg.encode())

        elif msg == "DONE":
            if current_obj_node:
                current_obj_node.remove()
                current_obj_node = None
            supervisor.step(500)
            spawn_object()