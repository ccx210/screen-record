import numpy as np
import ImageGrab
import cv2
from ctypes import *
import pythoncom
import pyHook
import win32clipboard
import time
import threading
import win32api

user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi
isEnd = False
mutex=threading.Lock()

#This is the callback function that activates when a KeyDonw message is sent. 
#It end the recording loop by setting the isEnd flag into True.
#I know it's very not elegant to do it like this but I had problems handling the work in the "right way".
def KeyStroke(event):
	#Shared mutex that ensure two threads don't conflict while accessing the isEnd flag.
	global mutex
	#Flag that controls when the recording loop breaks.
	global isEnd
	#Check the key. Stops when "shift+4($)" is sent.
	if event.Ascii == ord('$'):
		if mutex.acquire():#get the mutex
			isEnd = True#set the flag
			mutex.release()#release the mutex
			#This is the ugliest part!!! According to the pythoncom documents, pythoncom.PumpMessages() won't stop until get an WM_QUIT message.
			#I tried to send the message at the end of ScreenRecord() but failed.
			#Also attempt to put pythoncom.PumpMessages() into a thread but that caused it can't receive any message.
			
			#Assume that the ScreenRecord() will end in 2 seconds after the isEnd flag is changed.
			time.sleep(2)
			win32api.PostQuitMessage(0)
	return True

def ScreenRecord():
	#Shared mutex that ensure two threads don't conflict while accessing the isEnd flag.
	global mutex
	#Flag that controls when the recording loop breaks.
	global isEnd
	
	#cv2.namedWindow('window')
	#Grab a screen shot to get the current resolution of the screen.
	printscreen_pil =  ImageGrab.grab()
	#Tramsform PIL type image into cv type image
	printscreen_numpy = np.array(printscreen_pil.getdata(),dtype='uint8').reshape((printscreen_pil.size[1],printscreen_pil.size[0],3))
	result = printscreen_numpy
	height,width,layers = result.shape
	
	#Create a VideoWriter, users will be able to customiz the parameters in later versions.
	#writer = cv2.VideoWriter('sr.avi',cv2.cv.CV_FOURCC('P','I','M','I'),1,(width,height))
	writer = cv2.VideoWriter('sr.avi',-1,1,(width,height))
	
	#Sleep for 1 second to skip the encoder choosing dialog.
	time.sleep(1)
	#Grab the screen and encode it into the video, loop. 
	#No fps control yet.
	while(True):
		printscreen_pil =  ImageGrab.grab()
		printscreen_numpy = np.array(printscreen_pil.getdata(),dtype='uint8').reshape((printscreen_pil.size[1],printscreen_pil.size[0],3))
		#Flip the color from RGB to BGR
		result = printscreen_numpy
		result[:,:,[0,2]]=result[:,:,[2,0]]
		#result = cv2.cvtColor(printscreen_numpy,cv2.COLOR_RGB2BGR)	
		writer.write(result)
		#time.sleep(1.0/24)
		if mutex.acquire():
			print isEnd
			if isEnd:
				mutex.release()
				break
			else:
				mutex.release()
		#cv2.imshow('window',result)
		#if cv2.waitKey(25) & 0xFF == ord('q'):
		#	cv2.destroyAllWindows()
		#	break
	writer.release()
	
	
	return True
	
# create and register hook function manager
kl = pyHook.HookManager()
kl.KeyDown = KeyStroke

# regester hook for keyboard and loop
kl.HookKeyboard()




thread_screen = threading.Thread(target=ScreenRecord)
thread_screen.start()

#thread_hook = threading.Thread(target=pythoncom.PumpMessages)
#thread_hook.setDaemon(True)
#thread_hook.start()

pythoncom.PumpMessages()

