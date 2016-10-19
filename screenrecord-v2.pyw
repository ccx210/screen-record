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

def KeyStroke(event):
	global mutex
	global isEnd
	if event.Ascii == ord('$'):
		if mutex.acquire():
			isEnd = True
			mutex.release()
			time.sleep(1)
			win32api.PostQuitMessage(0)
	return True

def ScreenRecord():
	global mutex
	global isEnd
	
	#cv2.namedWindow('window')
	printscreen_pil =  ImageGrab.grab()
	printscreen_numpy = np.array(printscreen_pil.getdata(),dtype='uint8').reshape((printscreen_pil.size[1],printscreen_pil.size[0],3))
	result = cv2.cvtColor(printscreen_numpy,cv2.COLOR_BGR2RGB)
	height,width,layers = result.shape
	#writer = cv2.VideoWriter('sr.avi',cv2.cv.CV_FOURCC('P','I','M','I'),1,(width,height))
	writer = cv2.VideoWriter('sr.avi',-1,1,(width,height))
	while(True):
		printscreen_pil =  ImageGrab.grab()
		printscreen_numpy = np.array(printscreen_pil.getdata(),dtype='uint8').reshape((printscreen_pil.size[1],printscreen_pil.size[0],3))
		result = cv2.cvtColor(printscreen_numpy,cv2.COLOR_BGR2RGB)	
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

