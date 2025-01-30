from flask import Response, request
from flask import Flask
from flask import render_template
import threading
import time, socket, logging, traceback
from ivmlx import IVMLX
import cv2
import numpy as np
from picamera2 import Picamera2

outputFrame = None
thermcam = None
camera = None
lock = threading.Lock()
streaming = True
opacityValue = 0.3

thermalEnabled = True
cameraEnabled = True
fusionEnabled = True

app = Flask(__name__)

IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480
IMAGE_WIDTH = 800
IMAGE_HEIGHT = 600
FORMAT = "RGB888"

@app.route("/")
def index():
    return render_template("index.html",
    colormap_list=IVMLX.colormap_list,
    interpolation_list = IVMLX.interpolation_list)

@app.route("/start_stream")
def start_stream():
    global streaming
    streaming = True
    return("Stream started.")

@app.route("/stop_stream")
def stop_stream():
    global streaming
    streaming = False
    return("Stream stopped.")

@app.route("/enable_thermal")
def enable_thermal():
    global thermalEnabled
    thermalEnabled = True
    return("Thermal is enabled.")

@app.route("/disable_thermal")
def disable_thermal():
    global thermalEnabled
    thermalEnabled = False
    return("Thermal is disabled.")

@app.route("/enable_camera")
def enable_camera():
    global cameraEnabled
    cameraEnabled = True
    return("Camera is enabled.")

@app.route("/disable_camera")
def disable_camera():
    global cameraEnabled
    cameraEnabled = False
    return("Camera is disabled.")

@app.route("/video_feed")
def video_feed():

    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route('/colormap/<color_id>')
def change_colormap(color_id):
    thermcam.colormap_index = int(color_id)
    return ("Colormap changed to "+ str(color_id))

@app.route('/interpolation/<interpol_id>')
def change_interpolation(interpol_id):
    thermcam.interpolation_index = int(interpol_id)
    return ("Interpolation changed to "+ str(interpol_id))

@app.route('/opacity/<opacity_value>')
def change_opacity(opacity_value):
    global opacityValue
    opacityValue = int(opacity_value) / 100.0
    return(str(opacityValue))

def pull_images():
    global thermcam, outputFrame
    while thermcam is not None:
        thermal_frame = None
        camera_frame = None
        if streaming:
            if thermalEnabled:
                try:
                    thermal_frame = thermcam.update_image_frame()
                except Exception:
                    print("Too many retries error caught; continuing...")
            if cameraEnabled:
                try:
                    camera_frame = camera.capture_array()
                except Exception:
                    print("Camera frame error.")
        else:
            outputFrame = np.zeros((IMAGE_HEIGHT, IMAGE_WIDTH, 3), np.uint8)

        with lock:
            if thermalEnabled and not cameraEnabled:
                outputFrame = thermal_frame.copy()
            elif not thermalEnabled and cameraEnabled:
                outputFrame = camera_frame.copy()
            elif thermalEnabled and cameraEnabled and thermal_frame is not None and camera_frame is not None:
                outputFrame = cv2.addWeighted(thermal_frame, opacityValue, camera_frame, 1-opacityValue, 0)
            else:
                outputFrame = np.zeros((IMAGE_HEIGHT, IMAGE_WIDTH, 3), np.uint8)

def generate():
    global outputFrame

    while True:
        with lock:
            if outputFrame is None:
                continue
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            if not flag:
                continue

        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

def start_server():
    global thermcam, camera

    camera = Picamera2()
    camera.preview_configuration.main.size=(IMAGE_WIDTH, IMAGE_HEIGHT)
    camera.preview_configuration.main.format =  FORMAT
    camera.start()
    scaler = camera.camera_controls['ScalerCrop'][2:][0]
#    print(camera.camera_controls['ScalerCrop'])
    scaler = (200, 0, 2100, 1800)   # align for thermal sensor and camera's FOV.
    camera.set_controls({'ScalerCrop' : scaler})

    thermcam = IVMLX()
    time.sleep(0.1)
    t1 = threading.Thread(target=pull_images)
    t1.daemon = True
    t1.start()

    app.run(host="0.0.0.0", debug=True, threaded=True, use_reloader=False)

if __name__ == "__main__":
    start_server()