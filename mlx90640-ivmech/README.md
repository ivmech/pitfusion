# mlx90640-ivmech

This Python wrapper of the Melexis MLX90640 library was written for use with the Raspberry Pi and our [PitFusion module](https://www.ivmech.com/pitfusion). While you are free to use this software with whatever combination of device you choose.

## Raspberry Pi Users

** EXPERIMENTAL **

This port uses either generic Linux I2C or the  bcm2835 library.
Upon building, the mode is set with the I2C_MODE property, i.e. `make I2C_MODE=LINUX` or `make I2C_MODE=RPI`. The default is LINUX, without the need for the bcm2835 library or root access. We choose let it be default with I2C_MODE=LINUX.

### Generic Linux I2C Mode

Make sure the Linux I2C dev library is installed:

```text
sudo apt-get install libi2c-dev
```

To get the best out of your sensor you should modify `/boot/config.txt` and change your I2C baudrate.

The fastest rate recommended for compatibility with other sensors is 400kHz. This is compatible with SMBus devices:

```text
dtparam=i2c1_baudrate=400000
```

This will give you a framerate of - at most - 8FPS.

If you're just using the MLX90640 and, for example, the 1.12" OLED, you can safely use 1MHz:

```text
dtparam=i2c1_baudrate=1000000
```

This will give you a framerate of - at most - 32FPS.

Now build the MLX90640 library and examples in LINUX I2C mode:

```text
make clean
make I2C_MODE=LINUX
```

### BCM2835 Library Mode

To use the bcm2835 library, install like so:


```text
make bcm2835
```

Or, step by step:

```text
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.55.tar.gz
tar xvfz bcm2835-1.55.tar.gz
cd bcm2835-1.55
./configure
make
sudo make install
```

### Dependencies

libav for `video` example:


# Building

After installing the dependencies, you can build the library. Build-modes are:

* `make` or `make all`: build the library and all dependencies. Default is to use standard linux I2C-Drivers, specify Raspberry Pi driver with `make I2C_MODE=RPI`

* `sudo make install`: install libraries and headers into `$PREFIX`, default is `/usr/local`

