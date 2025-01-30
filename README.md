PitFusion
---
The **Pitfusion** is a cutting-edge dual-camera module developed for the Raspberry Pi, combining a **thermal imaging sensor (MLX90640)** and a **Raspberry Pi camera** into a single, compact device. This innovative module is designed to provide users with the ability to capture both **thermal and visual images simultaneously**, opening up a wide range of applications in fields such as **automation, robotics, security, and environmental monitoring**.

The **Pitfusion** module is a game-changer for Raspberry Pi enthusiasts and professionals, offering unparalleled flexibility and functionality for thermal and visual imaging projects. Explore its capabilities today and take your projects to the next level! 🚀
Getting Started
---
### Compatibility

Raspberry Pi OS Bookworm 12
### Installation

Update the packages.
```shell
sudo apt update
sudo apt upgrade
```

To get the best out of our sensor you should modify `/boot/firmware/config.txt` and change I2C baudrate.
```shell
sudo nano /boot/firmware/config.txt
```

```text
dtparam=i2c_arm=on
dtparam=i2c1_baudrate=1000000
```

Camera sensor is `Raspberry Pi Camera Module v1.3` therefore we need to specify `ov5647` in config.txt. Please find line `camera_auto_detect=1` and change it into as same below.
```text
camera_auto_detect=0
dtoverlay=ov5647
```

REBOOT
```shell
sudo reboot
```

Detecting module is connected.
```shell
i2cdetect -y 1
```

Output should be the same below.
```text
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- 33 -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- --    
```

Testing camera module is working.
```shell
libcamera-hello
```

Output should be the same below. If you have screen, camera view will be displayed.
```text
[0:45:24.849987679] [17630]  INFO Camera camera_manager.cpp:325 libcamera v0.3.2+99-1230f78d
[0:45:24.877456982] [17654]  WARN RPiSdn sdn.cpp:40 Using legacy SDN tuning - please consider moving SDN inside rpi.denoise
[0:45:24.879647690] [17654]  INFO RPI vc4.cpp:447 Registered camera /base/soc/i2c0mux/i2c@1/ov5647@36 to Unicam device /dev/media1 and ISP device /dev/media2
[0:45:24.879765855] [17654]  INFO RPI pipeline_base.cpp:1120 Using configuration file '/usr/share/libcamera/pipeline/rpi/vc4/rpi_apps.yaml'
[0:45:24.885965020] [17630]  INFO Camera camera.cpp:1197 configuring streams: (0) 800x600-RGB888 (1) 1296x972-SGBRG10_CSI2P
[0:45:24.886425920] [17654]  INFO RPI vc4.cpp:622 Sensor: /base/soc/i2c0mux/i2c@1/ov5647@36 - Selected sensor format: 1296x972-SGBRG10_1X10 - Selected unicam format: 1296x972-pGAA
```
### Dependencies

libi2c-dev, swig, swig4.0, python3-opencv, python3-matplotlib and cmapy.

Make sure the Linux I2C dev library is installed.
```shell
sudo apt install libi2c-dev
```

Install swig and swig4.0.
```shell
sudo apt install swig swig4.0
```

Install opencv python3 bindings.
```shell
sudo apt install python3-opencv
```

Install matplotlib
```shell
sudo apt install python3-matplotlib
```

Install cmapy (colormap) library.
```shell
git clone https://gitlab.com/cvejarano-oss/cmapy.git
cd cmapy
sudo python setup.py install
```
### Clone this Repository

```shell
git clone https://github.com/ivmech/pitfusion.git
```

### Building

After installing the dependencies, you can build the mlx90640 library which is needed.
```shell
cd pitfusion
cd mlx90640-ivmech
make
sudo make install
```

And build python module which is needed. Both ***swig*** and ***swig4.0*** are needed to compile python module.
```shell
cd python/library
sudo make install
```

Check is library is installed with command below.
```shell
pip list | grep MLX
```

Output should be the same below.
```text
MLX90640                           0.0.2
MLX90640                           0.0.2
```

### Usage

```shell
cd ~/pitfusion/WEB
python pitfusion_web.py
```


Video
---