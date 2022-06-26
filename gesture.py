from math import hypot
import numpy as np
import cv2

#Calcula la distancia entre dos puntos
def calculate_distance(x1, y1, x2, y2):
    p1 = np.array([x1, y1])
    p2 = np.array([x2, y2])
    return np.linalg.norm(p1 - p2)

#Detecta si se ha bajado el dedo índice
def detect_finger_down(hand_landmarks,frame,width,height):
    finger_down = False
    color_base = (255, 0, 112)
    color_index = (255, 198, 82)

    #Posición base(muñeca) punto 0
    x_base1 = int(hand_landmarks.landmark[0].x * width)
    y_base1 = int(hand_landmarks.landmark[0].y * height)

    #Posición base punto 9, es el cursor del ratón
    x_base2 = int(hand_landmarks.landmark[9].x * width)
    y_base2 = int(hand_landmarks.landmark[9].y * height)

    #Posición punta del dedo índice, punto 8
    x_index = int(hand_landmarks.landmark[8].x * width)
    y_index = int(hand_landmarks.landmark[8].y * height)

    #Calcular la distancia entre muñeca y base punto 9, punto del cursor
    distance_zero_nine = calculate_distance(x_base1, y_base1, x_base2, y_base2)
    #Calcular la distancia entre muñeca y punta del dedo índice
    distance_zero_index = calculate_distance(x_base1, y_base1, x_index, y_index)

    #Si hay menos distancia del dedo índice a muñeca que del cursor a muñeca = se ha bajado el dedo
    if distance_zero_index < distance_zero_nine:
        finger_down = True
        color_base = (255, 0, 255)
        color_index = (255, 0, 255)

    #Dinujar los puntos y las lineas
    cv2.circle(frame, (x_base1, y_base1), 5, color_base, 2)
    cv2.circle(frame, (x_index, y_index), 5, color_index, 2)
    cv2.line(frame, (x_base1, y_base1), (x_base2, y_base2), color_base, 3)
    cv2.line(frame, (x_base1, y_base1), (x_index, y_index), color_index, 3)

    return finger_down

#Encuentra la distancia entre dos puntos dados, método que usamos para el volumen
def findDistance (p1, p2,lmlist, img,draw=True,r=15,t=3):
        x1, y1 = lmlist[p1][0],lmlist[p1][1]
        x2, y2 = lmlist[p2][0],lmlist[p2][1]
        #Calculamos el punto del medio de los dos puntos dados
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        #Dibujar la linea entre ambos puntos, dibujar los puntos y el punto central
        if draw: 
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), t)
            cv2.circle(img, (x1, y1), r, (0, 255, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), r, (0, 255, 0), cv2.FILLED)
            cv2.circle(img, (cx, cy), r, (0, 255, 0), cv2.FILLED)
        
        length = hypot(x2 - x1, y2 - y1)

        return length, img, [x1, y1, x2, y2, cx, cy]

'''def getDistance(p1,p2):
    return hypot(p1[0] - p2[0],p1[1] - p2[1])

def isThumbNearIndexFinger(p1,p2):
    return getDistance(p1,p2) < 20
'''
#Este método detecta los gestos, podemos añadir todos los que deseamos
def simpleGesture(fingers,p1,p2):
    f_list = ['FIST!','ONE!','TWO!','THREE!','FOUR!','FIVE!'] 
    if fingers[0]==False and fingers[1]==True and fingers[2]==False and fingers[3]==False and fingers[4]==True:
        return 'ROCK!'
    elif fingers[0]==True and fingers[1]==True and fingers[2]==False and fingers[3]==False and fingers[4]==True:
        return 'SPIDERMAN!'
    elif fingers[0]==False and fingers[1]==True and fingers[2]==True and fingers[3]==False and fingers[4]==False:
        return 'PEACE!'
    elif fingers[0]==True and fingers[1]==False and fingers[2]==False and fingers[3]==False and fingers[4]==True:
        return 'TELEPHONE!'
    elif fingers[0]==True and fingers[1]==False and fingers[2]==False and fingers[3]==False and fingers[4]==False:
        return 'Pulgar arriba -> OK'
    else:
        return f_list[fingers.count(True)]