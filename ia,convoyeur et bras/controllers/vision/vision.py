from controller import Robot
import numpy as np
import cv2
from ultralytics import YOLO

robot = Robot()
timestep = int(robot.getBasicTimeStep())

cam = robot.getDevice("camera")
cam.enable(timestep)

emitter = robot.getDevice("emitter")
emitter.setChannel(1)  

ds = robot.getDevice("sensor")
ds.enable(timestep)

model = YOLO("../../models/yolo26n.pt")
WATER_LABELS = ["bottle"]
SODA_LABELS = ["cup", "can"]

while robot.step(timestep) != -1:
    # Lecture du capteur
    val = ds.getValue()
    
    # Si la valeur est < 1000, c'est qu'il y a un obstacle devant
    # (Avec ma lookupTable : 1000 = rien, 0 = collision)
    if val < 900:
        image = cam.getImage()
        w, h = cam.getWidth(), cam.getHeight()
        frame = np.frombuffer(image, np.uint8).reshape((h, w, 4))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        
        results = model(frame, verbose=False)
        
        if results[0].boxes:
            cls_id = int(results[0].boxes[0].cls[0])
            label = model.names[cls_id]
            
            if label in WATER_LABELS:
                print("VISION : EAU DETECTEE")
                emitter.send("WATER".encode())
                robot.step(2000) # Pause pour éviter le spam
            elif label in SODA_LABELS:
                print("VISION : SODA DETECTE")
                emitter.send("SODA".encode())
                robot.step(2000)

        cv2.imshow("YOLO", frame)
        cv2.waitKey(1)
