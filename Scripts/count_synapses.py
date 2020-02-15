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


class SynapseCounter(object):
    def __init__(self):
        self.meta_data = dict()
        self.load_data('./Data/Atta/CG379_24_63xZ2_Ca_re_2/')

    def load_data(self, filepath: str = None):
        paths = Path(filepath)
        print(paths)
        image_paths = [i for i in paths.iterdir() if '.tif' in str(i)]
        meta_data_path = [i for i in paths.iterdir() if '.txt' in str(i)]

        images = ImageSequence(image_paths, as_grey=True)
        self.images = self.grey_sequence(images)

        plt.imshow(self.images[4])
        plt.show()
        
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

if __name__ == '__main__':
    sc = SynapseCounter()
    print(f'blubb')
