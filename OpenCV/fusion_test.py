import os
import time
import numpy
import cv2
import colorsys
import MLX90640 as thermalcamera
from threading import Thread
from picamera2 import Picamera2

#WIDTH = 1920
#HEIGH = 1080
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480
FORMAT = "RGB888"
THERMAL_WIDTH = 32
THERMAL_HEIGHT = 24
SCALE = IMAGE_WIDTH / THERMAL_WIDTH

WINDOW = "Pit FUSION"
SETTINGS = "Settings"

PATH = os.getcwd()
FILE_OUTPUT = "output.avi"

class ThermalCamera:

    def __init__(self, src=0):
        self.thermalcamera = thermalcamera
        self.thermalcamera.setup(16)
        self.frame = self.thermalcamera.get_frame()
        self.stopped = False

    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while not self.stopped:
            self.frame = self.thermalcamera.get_frame()

    def stop(self):
        self.stopped = True


class Fusion:

    def __init__(self):
        self.temperature = 0
        self.mouse_x = IMAGE_WIDTH/2
        self.mouse_y = IMAGE_HEIGHT/2

        # create blank image for thermal camera frame
        self.blank_image = numpy.zeros((THERMAL_HEIGHT, THERMAL_WIDTH, 3), numpy.uint8)

        # initialize raspberry pi camera module
        self.camera = Picamera2()
        self.camera.preview_configuration.main.size=(IMAGE_WIDTH, IMAGE_HEIGHT)
        self.camera.preview_configuration.main.format =  FORMAT
        self.camera.start()
        scaler = self.camera.camera_controls['ScalerCrop'][2:][0]
        self.camera.set_controls({'ScalerCrop' : scaler})
#        self.rawcapture = PiRGBArray(self.camera, size=(IMAGE_WIDTH, IMAGE_HEIGHT))

        # initialize thermal camera threading
        self.thermalcamera = ThermalCamera().start()

        self.record_out = cv2.VideoWriter(FILE_OUTPUT, cv2.VideoWriter_fourcc(*'X264'), 15.0, (IMAGE_WIDTH, IMAGE_HEIGHT))

        time.sleep(0.1)

        self.window_setup()

    def window_setup(self):

        cv2.namedWindow(WINDOW)
        cv2.namedWindow(SETTINGS)
        cv2.createTrackbar("PALLETE", SETTINGS, 48, 100, self.nothing)
        cv2.createTrackbar("THRESHOLD", SETTINGS, 30, 200, self.nothing)
        cv2.createTrackbar("OPACITY THERMAL", SETTINGS, 80, 100, self.nothing)
    #    cv2.createTrackbar("OPACITY CAMERA", SETTINGS, 0, 100, self.nothing)
        self.switch_temp = 'TEMPERATURE\n0 : OFF \n1 : ON'
        cv2.createTrackbar(self.switch_temp, SETTINGS, 0, 1, self.nothing)
        cv2.createTrackbar("MODE", SETTINGS, 1, 3, self.nothing)

        self.switch_record = 'RECORD\n0 : OFF \n1 : ON'
        cv2.createTrackbar(self.switch_record, SETTINGS, 0, 1, self.nothing)

        #cv2.setTrackbarPos("PALLETE", SETTINGS, 48)
        #cv2.setTrackbarPos("THRESHOLD", SETTINGS, 30)
        #cv2.setTrackbarPos("OPACITY THERMAL", SETTINGS, 80)
        #cv2.setTrackbarPos("OPACITY CAMERA", SETTINGS, 30)
        #cv2.setTrackbarPos("MODE", SETTINGS, 1)

    def main(self):
        while True:
            camera_image = self.camera.capture_array()

            pallete = cv2.getTrackbarPos('PALLETE', SETTINGS) / 10.0
            if pallete < 1.0:
                pallete = 1.0
                cv2.setTrackbarPos("PALLETE", SETTINGS, 10)
            temp_threshold = cv2.getTrackbarPos('THRESHOLD', SETTINGS)
            opacity_thermal = cv2.getTrackbarPos("OPACITY THERMAL", SETTINGS) / 100.0
    #        opacity_camera = cv2.getTrackbarPos("OPACITY CAMERA", WINDOW) / 100.0
            mode = cv2.getTrackbarPos("MODE", SETTINGS)
            show_temperature = cv2.getTrackbarPos(self.switch_temp, SETTINGS)
            record_streaming = cv2.getTrackbarPos(self.switch_record, SETTINGS)

            if mode == 0:
                image = camera_image

            if mode in [1, 2]:
                thermal_frame = self.thermalcamera.frame

                for y in range(THERMAL_HEIGHT):
                    for x in range(THERMAL_WIDTH):
                        value = thermal_frame[THERMAL_WIDTH * (THERMAL_HEIGHT-1-y) + x]
                        if x == (self.mouse_x/SCALE) and y == (self.mouse_y/SCALE): self.temperature = value

                        if value < temp_threshold and mode==2:
                            self.blank_image[y, x] = (255,255,255)
                        else:
                            self.blank_image[y, x] = self.temp_to_col(value, pallete)


                self.blank_image = cv2.cvtColor(self.blank_image, cv2.COLOR_RGB2BGR)
                thermal_image = cv2.resize(self.blank_image, (IMAGE_WIDTH, IMAGE_HEIGHT), interpolation=cv2.INTER_CUBIC)

                image = cv2.addWeighted(thermal_image, opacity_thermal, camera_image, 1.0-opacity_thermal, 0)


            if show_temperature == 1:
                # OVERLAY TEMPERATURE TEXT
                font = cv2.FONT_HERSHEY_TRIPLEX
                cv2.putText(image, str(round(self.temperature, 2)) +' C', (self.mouse_x+5, self.mouse_y-5), font, 0.8, (25,25,25), 2, cv2.LINE_AA)
                # MOUSE CLICK CENTER
                cv2.circle(image, (self.mouse_x, self.mouse_y), 10, (25,25,25), 1)

            cv2.imshow(WINDOW, image)
            cv2.setMouseCallback(WINDOW, self.onMouse)

            #cv2.imshow("CAMERA", camera_image)
            #cv2.imshow("THERMAL", thermal_image)

            if record_streaming == 1:
                self.record_out.write(image)

            key = cv2.waitKey(1) & 0xFF
#            self.rawcapture.truncate(0)

            if key == ord("q"):
                self.record_out.release()
                self.thermalcamera.stop()
                break

    # colorize
    def temp_to_col(self, value, threshold):
        hue = (180 - (value * threshold)) / 360.0
        try:
            return tuple([int(c*255) for c in colorsys.hsv_to_rgb(hue, 1.0, 1.0)])
        except:
            return (0,0,0)

    #grayscale
    def temp_to_gray(self, val):
        try:
            return tuple([int(c*255) for c in colorsys.hsv_to_rgb(1.0, 0.0, val/70.0)])
        except:
            return 0

    def onMouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.mouse_x = x
            self.mouse_y = y

    def nothing(self, x):
        pass

if __name__ == "__main__":
    app = Fusion()
    app.main()


def temp_to_col(value, threshold):
    hue = (180 - (value * threshold)) / 360.0
    try:
        return tuple([int(c*255) for c in colorsys.hsv_to_rgb(hue, 1.0, 1.0)])
    except:
        return (0,0,0)
#picam2 = Picamera2()
#picam2.preview_configuration.main.size=(WIDTH, HEIGH) #full screen : 3280 2464
#picam2.preview_configuration.main.format =  FORMAT#8 bits
#picam2.start()
#scaler = picam2.camera_controls['ScalerCrop'][2:][0]
#picam2.set_controls({'ScalerCrop' : scaler})

#while True:
#	im = picam2.capture_array()
#	cv2.imshow("preview",im)
#	if cv2.waitKey(1)==ord('q'):
#		break

#picam2.stop()
#cv2.destroyAllWindows()
