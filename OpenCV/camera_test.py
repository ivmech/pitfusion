import cv2
from picamera2 import Picamera2

#WIDTH = 1920
#HEIGH = 1080
WIDTH = 640
HEIGH = 480
FORMAT = "XRGB8888"

picam2 = Picamera2()
picam2.preview_configuration.main.size=(WIDTH, HEIGH) #full screen : 3280 2464
picam2.preview_configuration.main.format =  FORMAT#8 bits
picam2.start()
scale = picam2.camera_controls['ScalerCrop'][2:][0]
picam2.set_controls({'ScalerCrop' : scale})

while True:
	im = picam2.capture_array()
	cv2.imshow("preview",im)
	if cv2.waitKey(1)==ord('q'):
		break

picam2.stop()
cv2.destroyAllWindows()
