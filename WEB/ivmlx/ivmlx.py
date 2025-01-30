import cv2
import cmapy
import numpy as np
import MLX90640 as mlx

THERMAL_WIDTH = 32
THERMAL_HEIGHT = 24
IMAGE_WIDTH = 800
IMAGE_HEIGHT = 600

class IVMLX:
    colormap_list=['jet','rainbow','nipy_spectral','bwr','seismic','PiYG_r','tab10','tab20','gnuplot2', 'viridis', 'CMRmap_r', 'Greys_r']
    interpolation_list=[cv2.INTER_NEAREST, cv2.INTER_LINEAR, cv2.INTER_AREA, cv2.INTER_CUBIC, cv2.INTER_LANCZOS4, 5, 6]

    temp_min=None
    temp_max=None
    raw_image=None
    image=None

    def __init__(self):
        self.colormap_index = 0
        self.interpolation_index = 0
        mlx.setup(16)

    def update_image_frame(self):
        self.retrieve_raw_image()
        self.process_raw_image()
        return self.image

    def retrieve_raw_image(self):
        self.raw_image = np.array(mlx.get_frame())
        self.temp_min = np.min(self.raw_image)
        self.temp_max = np.max(self.raw_image)
        self.temperature_to_uints()

    def temperature_to_uints(self):
        self.raw_image = np.nan_to_num(self.raw_image)
        self.raw_image = np.uint8((self.raw_image - self.temp_min)*255/(self.temp_max-self.temp_min))
        self.raw_image.shape = (THERMAL_HEIGHT, THERMAL_WIDTH)
#        self.raw_image.shape = (THERMAL_WIDTH, THERMAL_HEIGHT)
#        return norm

    def process_raw_image(self):
        self.image = cv2.applyColorMap(self.raw_image, cmapy.cmap(self.colormap_list[self.colormap_index]))
        self.image = cv2.flip(self.image, 0)
        self.image = cv2.resize(self.image, (IMAGE_WIDTH, IMAGE_HEIGHT), self.interpolation_list[self.interpolation_index])

    def change_colormap(self, forward:bool = True):
        """Cycle colormap. Forward by default, backwards if param set to false."""
        if forward:
            self.colormap_index+=1
            if self.colormap_index==len(self.colormap_list):
                self.colormap_index=0
        else:
            self.colormap_index-=1
            if self.colormap_index<0:
                self.colormap_index=len(self.colormap_list)-1

if __name__ == "__main__":
#    thermcam = IVMLX()
#    frame = thermcam.update_image_frame()
#    cv2.imshow("THERMAL", frame)
#    while True:
#        key = cv2.waitKey(1) & 0xFF
#        if key == ord("q"):
#            break
    pass