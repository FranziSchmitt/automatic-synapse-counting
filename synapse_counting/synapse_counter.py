import numpy as np

from skimage.feature import blob_dog, blob_log, blob_doh

import matplotlib.pyplot as plt
import seaborn as sns

sns.set()


class SynapseCounter(object):
    def __init__(self):
        self.images = None
        self.final_images = list()
        self.meta_data = dict()

    @staticmethod
    def laplacian_of_gaussian(image):
        minimum = 2
        maximum = 30
        threshold = 0.2
        num_sigma = 200
        overlap = 0.7

        blobs_log = blob_log(
            image,
            min_sigma=minimum,
            max_sigma=maximum,
            num_sigma=num_sigma,
            threshold=threshold,
            overlap=overlap
        )
        radii = [b[2] for b in blobs_log]

        return blobs_log, radii

    @staticmethod
    def _plot_log_blobs(blobs, image):
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))
        for blob in blobs:
            ax.imshow(image, interpolation='nearest')
            y, x, r = blob
            c = plt.Circle((x, y), r, color='yellow', linewidth=5, fill=False)
            ax.add_patch(c)
        ax.set_axis_off()
        plt.tight_layout()
        plt.show()

    @staticmethod
    def _analyse_blob_radii(radii):
        median = np.median(radii)
        mean = np.mean(radii)
        std = np.std(radii)
        return median, mean, std
