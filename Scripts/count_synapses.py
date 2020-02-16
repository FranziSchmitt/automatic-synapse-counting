import numpy as np
from pathlib import Path
from math import sqrt

from pims import ImageSequence
from skimage.color import rgb2grey
from skimage.feature import blob_dog, blob_log, blob_doh
from skimage.measure import find_contours

import matplotlib.pyplot as plt
import seaborn as sns

sns.set()

import pdb


class SynapseCounter(object):
    def __init__(self):
        self.images = None
        self.final_images = list()
        self.meta_data = dict()
        self.load_data('./Data/Atta/CG379_24_63xZ2_Ca_re_2/')
        self.adjust_sequence(
            y_start=400, x_start=200, lower_threshold=60, upper_threshold=100,
        )
        for image in self.final_images:
            self.laplacian_gaussian(image)

    def load_data(self, filepath: str = None):
        paths = Path(filepath)
        print(paths)
        image_paths = [i for i in paths.iterdir() if '.tif' in str(i)]
        meta_data_path = [i for i in paths.iterdir() if '.txt' in str(i)]

        images = ImageSequence(image_paths, as_grey=True)
        self.images = self.grey_sequence(images)

        # plt.imshow(self.images[4])
        # plt.show()

        with open(meta_data_path[0], 'r', encoding='latin-1') as fid:
            text_file = fid.readlines()

        for line in text_file:
            if 'Voxel-Height' in line.split():
                self.meta_data['voxel_size'] = float(line.split()[-1][:-1])
            elif 'Voxel_Depth' in line.split():
                self.meta_data['voxel_depth'] = float(line.split()[-1][:-1])

    @staticmethod
    def grey_sequence(rgb_sequence: list) -> list:

        grey_images = []
        for image in rgb_sequence:
            grey_image = rgb2grey(image)
            grey_images.append(grey_image)

        return grey_images

    def adjust_sequence(
        self,
        y_start: int,
        x_start: int,
        lower_threshold: int,
        upper_threshold: int,
    ):

        self.cropped_images = list()

        pixel_number = 10 / self.meta_data['voxel_size']

        y_stop = int(y_start + pixel_number)
        x_stop = int(x_start + pixel_number)

        cropped_images = [
            i[y_start:y_stop, x_start:x_stop] for i in self.images
        ]

        for im in cropped_images:
            image = im.copy()
            image[image < lower_threshold] = 0
            image[image > upper_threshold] = 100000
            self.final_images.append(image)

    @staticmethod
    def laplacian_gaussian(image):
        minima = np.linspace(0, 10, 10)
        maxima = np.linspace(20, 60, 10)
        numbers = np.linspace(5, 15, 10)
        thresholds = np.linspace(0.05, 0.15, 10)
        parameters = list(zip(minima, maxima, numbers, thresholds))
        blobs = {}

        for i, params in enumerate(parameters):
            blobs_log = blob_log(
                image,
                min_sigma=int(params[0]),
                max_sigma=int(params[1]),
                num_sigma=int(params[2]),
                threshold=int(params[3]),
            )
            blobs[i] = [blobs_log, params]
        
        radii = {}
        for i, b in blobs.items():
            log_blobs = blobs[i][0]
            radii[i] = [b[2] for b in log_blobs]
        
        for r in radii.values():
            median = np.median(r)
            mean = np.mean(r)
            std = np.std(r)
            print(median, mean, std)

        fig, axes = plt.subplots(
            2, 5, figsize=(15, 30), sharex=True, sharey=True
        )
        ax = axes.ravel()

        for i, blob in blobs.items():
            ax[i].set_title(f'{blobs[i][1]}')
            ax[i].imshow(image, interpolation='nearest')
            log_blobs = blobs[i][0]
            for b in log_blobs:
                y, x, r = b
                c = plt.Circle(
                    (x, y), r, color='yellow', linewidth=3, fill=False
                )
                ax[i].add_patch(c)
            ax[i].set_axis_off()
        plt.tight_layout()
        plt.show()


if __name__ == '__main__':
    sc = SynapseCounter()
