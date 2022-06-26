from xmlrpc.client import FastUnmarshaller
import cv2
import mediapipe as mp
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import keyboard
import numpy as np
import gesture
import time
import pyautogui

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
#Color utilizado para el punto de la mano que marca el cursor
color_mouse = (255, 0, 255)

# Inicializa los altavoces como dispositivo y coge el volumen max y min a lo que pueden llegar
dispositivos= AudioUtilities.GetSpeakers()#initialization for using pycaw
interface = dispositivos.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange=volume.GetVolumeRange()
minVol=volRange[0]
maxVol=volRange[1]

#Para dividir la pantalla en distintas lineas
right= 480
left = 160

#Tamaño pantalla de nuestro computador
SCREEN_X_INI = 0
SCREEN_Y_INI = 0
SCREEN_X_FIN = 1360
SCREEN_Y_FIN = 770

aspect_screen = (SCREEN_X_FIN - SCREEN_X_INI) / (SCREEN_Y_FIN - SCREEN_Y_INI)

#Según como situa los puntos de las manos Mediapipe son la punta d elos cinco dedos de la mano
lms = [4,8,12,16,20]

with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7) as hands:

    while True:
        ret, frame = cap.read()
        if ret == False:
            break

        height, width, _ = frame.shape
        frame = cv2.flip(frame, 1)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        #Dibujamos las lineas que separan las pantallas
        cv2.line(frame, (left,0),(left, frame.shape[0]),(25,25,255), 2)
        cv2.line(frame, (right,0),(right, frame.shape[0]),(25,25,255), 2)

        results = hands.process(frame_rgb)
        lmList = []
        #Obtenemos las posiciones de los puntos claves
        if results.multi_hand_landmarks is not None:
            for hand_landmarks in results.multi_hand_landmarks:
                for lm in hand_landmarks.landmark:
                    h,w,_ = frame.shape
                    lmList.append([int(lm.x*w),int(lm.y*h)])
        
        #Una vez tenemos las posiciones calcular que dedos están levantados
        if len(lmList):
            fingers = []
            if lmList[5][0] < lmList[17][0]:
                fingers.append(True) if lmList[lms[0]][0] < lmList[lms[0]-2][0] else fingers.append(False)    
            else:
                fingers.append(True) if lmList[lms[0]][0] > lmList[lms[0]-2][0] else fingers.append(False)
            for lm in range(1,len(lms)):
                    fingers.append(True) if lmList[lms[lm]][1] < lmList[lms[lm]-2][1] else fingers.append(False) 

            #Parte derecha de la imagen
            if lmList[0][0] > right:
                #Avanzar diapositiva
                if gesture.simpleGesture(fingers,lmList[4],lmList[8]) == 'FIVE!': 
                    keyboard.press('down')
                    time.sleep(2)
                #Varianción volumen
                if len(fingers):
                    if fingers[0] == True & fingers[1] == True:
                        longitud,frame,linea = gesture.findDistance(4,8,lmList,frame,r=8,t=2)
                        vol=np.interp(longitud,[5,100],[minVol,maxVol])
                        volume.SetMasterVolumeLevel(vol,None)

            #Parte izquierda de la imagen
            if lmList[0][0] < left : 
                #Volver a diapositiva anterior
                if gesture.simpleGesture(fingers,lmList[4],lmList[8]) == 'FIVE!': 
                    keyboard.press ('up')
                    time.sleep(2)
            #Parte central de la imgen
            else : 
                #Interacción del ratón
                area_width = width - 160 * 2
                area_height = int(area_width / aspect_screen)
                xm = np.interp(lmList[9][0], (160, 160 + area_width), (SCREEN_X_INI, SCREEN_X_FIN))
                ym = np.interp(lmList[9][1], (160, 160 + area_height), (SCREEN_Y_INI, SCREEN_Y_FIN))
                pyautogui.moveTo(int(xm), int(ym))
                if gesture.detect_finger_down(hand_landmarks,frame,width,height):
                    pyautogui.click()
                cv2.circle(frame, (lmList[9][0], lmList[9][1]), 10, color_mouse, 3)
                cv2.circle(frame, (lmList[9][0], lmList[9][1]), 5, color_mouse, -1)

                #Inicia la presentación
                if gesture.simpleGesture(fingers,lmList[4],lmList[8]) == 'SPIDERMAN!' :
                    keyboard.press('f5')
                    
                
    
        cv2.imshow('output', frame)
        #Pulsar "esc" para cerrar la aplicación
        if cv2.waitKey(1) & 0xFF == 27:
            break
cap.release()
cv2.destroyAllWindows()
