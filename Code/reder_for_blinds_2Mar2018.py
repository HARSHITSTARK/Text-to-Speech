import imutils
import cv2
from PIL import *
from pytesseract import *
import time
from skimage.filter import threshold_adaptive
import numpy as np
import Image
import os
import Adafruit_CharLCD as LCD
import RPi.GPIO as GPIO
from datetime import datetime
import subprocess
import re

##os.system("tvservice -o")
##os.system("tvservice -p; fbset -depth 8; fbset -depth 16")

speaking = False
button_pressed = False

def speak(text):
    os.system("pico2wave --lang=en-US -w sample2.wav \"" + text + "\" && aplay sample2.wav")
    os.remove("sample2.wav")

def read(text):   
    p = subprocess.call("pico2wave --lang=en-US -w sample.wav \"" + text + "\"",shell = True)
    player = subprocess.Popen(["aplay", "sample.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    player.wait()
##    os.remove("sample.wav")
        
def isr(channel):
    print ("interrupt detected")
    button_pressed = True
    read(" ")
        
button = 2

GPIO.setup(button,GPIO.IN)

GPIO.add_event_detect(button,GPIO.FALLING,callback=isr,bouncetime=1000)

# Raspberry Pi pin configuration:
lcd_rs        = 21  # Note this might need to be changed to 21 for older revision Pi's.
lcd_en        = 20
lcd_d4        = 16
lcd_d5        = 12
lcd_d6        = 7
lcd_d7        = 8
##lcd_backlight = 16

# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows    = 2

lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows)

IMAGE_FILE='sample.jpg'

reset = True


while reset == True:

    try:

        main = True
        lcd.set_backlight(0)
        lcd.clear()
        print ("Raspberry pi Reader for blinds")
        lcd.message('  Raspberry pi\nReader For blind')
        speak("Raasspberry pi, Reader, for blinds.")
        time.sleep(2)
        
        t1 = datetime.now()
        while GPIO.input(button) == False:
            t2 = datetime.now()
            delta = t2 - t1
            time_elapse = delta.total_seconds()
            if time_elapse > 15:
                reset = False
                main = False
                break

        if main:    
            lcd.clear()
            lcd.message('Searching for\nCamera')
            print ("Searching for Camera")
            speak("Searching for Camera.")
            time.sleep(2)

            camera=cv2.VideoCapture(0)

            ret = camera.set(3,640)
            ret = camera.set(4,480)
            
            if not camera.isOpened():
                main = False
                print ("can't open the camera")
                lcd.clear()
                lcd.message('Error:Camera not\nFound')
                time.sleep(2)
                lcd.clear()
                lcd.message('Connect Camera &\npress reset')
                speak("Camera not Found, Connect Camera & press reset.")
                while GPIO.input(button) == True:
                    None
            
            else:
                main = True
                print ("camera found")
                lcd.clear()
                lcd.message('Found Camera')
                speak("camera founded.")
                time.sleep(2)
                camera.release()
                
        while main:
                                
            lcd.clear()
            lcd.message('Press switch...')
            speak("Place the paper, and press the switch")
            time.sleep(1)    
            
            camera=cv2.VideoCapture(0)

            ret = camera.set(3,640)
            ret = camera.set(4,480)
            while not camera.isOpened():
                None
            while True:
                ret,img = camera.read()
                cv2.imwrite('face0.jpeg',img)
                cv2.imshow('img', img)
                cv2.waitKey(1)
                if GPIO.input(button) == False:
                    break

            lcd.clear()
            lcd.message("Capturing Image.")
            speak("Capturing Image")
            time.sleep(2)
            
            ret, img = camera.read()

            camera.release()
            cv2.imwrite("test1.jpeg",img)
            
            warped = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            warped = threshold_adaptive(warped, 251, offset = 10)
            warped = warped.astype("uint8") * 255

            time.sleep(1)
            lcd.clear()
        
            
            lcd.message("Image captured")
            speak("Image captured.")
            time.sleep(1)
            # show the original and scanned images
            print ("STEP 3: Apply perspective transform")

            lcd.clear()
            lcd.message('Processing...')
            speak("Processing for the speech.")
            time.sleep(2)
            cv2.imwrite(IMAGE_FILE,warped)

            img = Image.open(IMAGE_FILE)
            print ("converting to text")
            words = image_to_string(img).strip()
            print ("converted to text")
                                      
            if len(words) > 0:

                speak("Process complete, Press switch to \nstop playing.")
                words = words.replace('\n',' ')
                speech = re.sub('[^a-zA-Z0-9 \n\.\,]','',words)
                print ("words" , speech)
                read(speech)
                time.sleep(2)
                lcd.clear()
                lcd.message('Press switch to \nstop playing')
                speak("speech completed.")
                
            else:
                
                lcd.clear()
                lcd.message('No text Found...')
                speak("No text Found.")
                time.sleep(3)
                        
                       
            if GPIO.input(button) == False:
                    break
                
    except Exception as e:
        print (e)
        print ("got error")
        print ("press reset")
        lcd.clear()
        lcd.message('   !!!!Error!!!!   ')

        while GPIO.input(button):
            lcd.set_cursor(0,1)
            lcd.message('    Press reset     ')
            time.sleep(0.5)
            lcd.set_cursor(0,1)
            lcd.message('                    ')
            time.sleep(0.5)

        t1 = datetime.now()
        while GPIO.input(button) == False:
            t2 = datetime.now()
            delta = t2 - t1
            time_elapse = delta.total_seconds()
            if time_elapse > 5:
                main = False
                reset = False
                break

print ("end")
##os.system("tvservice -p; fbset -depth 8; fbset -depth 16")
lcd.message('Program Terminate')
time.sleep(2)
lcd.clear()
GPIO.cleanup()

