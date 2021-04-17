import argparse
import math
from pathlib import Path
from typing import List, Dict, Optional, Union

import numpy as np
from pims import ImageSequence
from shapely.geometry import Point
from skimage.color import rgb2grey
from matplotlib import patches

from skimage.feature import blob_log

import matplotlib.pyplot as plt
import seaborn as sns

sns.set()

# local constants
VOXEL_HEIGHT = "Voxel-Height"


class SynapseCounter(object):
    image_sequence: List[np.ndarray]
    meta_data: Dict[str, float]
    blobs = Dict[int, List[float]]
    num_synapses = int

    def __init__(self):
        self.left = 400
        self.top = 200
        self.length = 10
        self.min_pixel_value = 100
        self.max_pixel_value = 100
        self.meta_data = {}
        self.image_sequence = []
        self.blobs = {}
        self.num_synapses = 0

    def count_synapses(
        self,
        filepath: Union[str, Path],
        left: Optional[int] = None,
        top: Optional[int] = None,
        length: Optional[int] = None,
        min_threshold: Optional[int] = None,
        max_threshold: Optional[int] = None,
        visualize_result: bool = True
    ):
        self._load_data(filepath=filepath)
        if left:
            self.left = left
        if top:
            self.top = top
        if length:
            self.length = length
        if min_threshold:
            self.min_pixel_value = min_threshold
        if max_threshold:
            self.max_pixel_value = max_threshold

        self._apply_laplacian_of_gaussian_to_images()
        overlapping = self._count_synapses()

        if visualize_result:
            result_path = filepath / "result"
            self._visualize_result(result_path, overlapping)

    def _load_data(self, filepath: Union[str, Path]):
        if type(filepath) == str:
            filepath = Path(filepath)

        if not filepath.is_dir():
            raise ValueError(f'The path you provided does not exist: {filepath}.')

        paths = Path(filepath)
        image_paths = list(paths.glob("*.tif"))
        try:
            meta_data_path = list(paths.glob("*.txt"))[0]
        except IndexError:
            raise ValueError(f'Could not find a metadata file in {filepath}. Expected to find a .txt file there.')
        if not image_paths:
            raise ValueError(f"Could not find any tif image files in {filepath}")

        with meta_data_path.open("r", encoding="latin-1") as fid:
            text_file = fid.readlines()

        for line in text_file:
            if VOXEL_HEIGHT in line.split():
                self.meta_data[VOXEL_HEIGHT] = float(line.split()[-1][:-1])

        if VOXEL_HEIGHT not in self.meta_data:
            raise ValueError(f'Unable to find voxel height in {meta_data_path}')

        images = ImageSequence(list(image_paths), as_grey=True)
        grey_images = self._get_grey_sequence(images)
        self._threshold_and_crop_images(grey_images)

    @staticmethod
    def _get_grey_sequence(rgb_sequence: ImageSequence) -> List[ImageSequence]:
        grey_images = []
        for image in rgb_sequence:
            grey_image = rgb2grey(image)
            grey_images.append(grey_image)

        return grey_images

    def _threshold_and_crop_images(self, images: List[ImageSequence]) -> None:
        pixel_number = self.length / self.meta_data[VOXEL_HEIGHT]

        y_stop = int(self.top + pixel_number)
        x_stop = int(self.left + pixel_number)

        cropped_images = [i[self.top : y_stop, self.left : x_stop] for i in images]

        for im in cropped_images:
            image = im.copy()
            image[image <= self.min_pixel_value] = 0
            image[image > self.max_pixel_value] = (
                image[image > self.max_pixel_value] - self.max_pixel_value
            )
            image = image / np.max(image)
            self.image_sequence.append(image)

    def _apply_laplacian_of_gaussian_to_images(self):
        for i in range(len(self.image_sequence)):
            image = self.image_sequence[i]
            min_sigma = 5
            max_sigma = 9
            f = blob_log(
                image,
                min_sigma=min_sigma,
                max_sigma=max_sigma,
                num_sigma=(max_sigma - min_sigma),
                threshold=0.1,
            )

            self.blobs[i] = []
            for blob in f:
                blob_center = Point(blob[0], blob[1])
                blob_center.buffer = blob[2]
                self.blobs[i].append(blob_center)

    def _count_synapses(self):
        overlapping = []
        for key in range(len(self.blobs.keys()) - 1):
            blobs_1 = self.blobs[key]
            blobs_2 = self.blobs[key + 1]
            for blob in blobs_1:
                if blob not in overlapping:
                    for blob_2 in blobs_2:
                        allowed_dist = (blob.buffer + blob_2.buffer) * 2 / 3
                        if blob.distance(blob_2) <= allowed_dist:
                            overlapping.extend([blob, blob_2])
                    self.num_synapses += 1
        last_key = max(self.blobs.keys())
        for blob in self.blobs[last_key]:
            if blob not in overlapping:
                self.num_synapses += 1
        return overlapping

    def _visualize_result(self, result_path: Path, overlapping: List):
        fig = plt.figure(figsize=(7, 20))
        ax = []
        number_of_images_to_show = len(self.image_sequence) + 1
        number_of_rows_in_plot = math.ceil(number_of_images_to_show / 2)
        for key in range(number_of_images_to_show):
            ax.append(
                plt.subplot2grid(
                    (number_of_rows_in_plot, 2), (math.floor(key / 2), key % 2)
                )
            )

        ax_big = plt.subplot2grid(
            (number_of_rows_in_plot, 2), (0, 0), colspan=2, rowspan=2
        )
        for key, value in self.blobs.items():
            im = self.image_sequence[key]
            ca = ax[key]

            ca.imshow(im, cmap="gray")
            for blob in value:
                ca.set_xticklabels([])
                ca.set_yticklabels([])
                color = "red" if blob in overlapping else "green"
                circle = plt.Circle(
                    (blob.y, blob.x), blob.buffer, color=color, linewidth=3, fill=False
                )
                ca.add_patch(circle)
            ca.set_title(f"synapse count: {len(value)}")
        iii = self.image_sequence[0]
        ax_big.imshow(iii, cmap="gray")
        width, height = iii.shape
        r = patches.Rectangle(
            (self.left, self.top), width, height, color="b", fill=False, linewidth=4
        )

        ax_big.add_patch(r)
        ax_big.set_xticks([])
        ax_big.set_yticks([])
        ax_big.set_title(f"Total synapse count: {self.num_synapses}")
        filename = f"blobs_{self.num_synapses}.png"
        savepath = result_path / filename
        result_path.mkdir(parents=True, exist_ok=True)
        fig.savefig(str(savepath))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automatic synapse counter.")
    parser.add_argument(
        "--input", "-i", help="Path to image stack and metadata",
    )
    parser.add_argument(
        "--left-x", "-x", default=None, help="X position to start at. defaults at 600."
    )
    parser.add_argument(
        "--top-y", "-y", default=None, help="Y position to start at. Defaults at 200."
    )
    parser.add_argument(
        "--length",
        "-l",
        default=None,
        help="Desired length of the evaluated square. Defaults at 10.",
    )
    parser.add_argument(
        "--upper-threshold",
        "-u",
        default=None,
        help="Upper threshold for thresholding. Defaults at 90.",
    )
    parser.add_argument(
        "--lower-threshold",
        "-w",
        default=None,
        help="Lower threshold for thresholding. Defaults at 50.",
    )
    parser.add_argument(
        "--save-results",
        "-s",
        default=True,
        help="Lower threshold for thresholding. Defaults at 50.",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    left_x = args.left_x
    top_y = args.top_y
    square_length = args.length
    upper_threshold = args.upper_threshold
    lower_threshold = args.lower_threshold
    save_result = args.save_results

    counter = SynapseCounter()
    counter.count_synapses(
        input_path,
        left=left_x,
        top=top_y,
        length=square_length,
        max_threshold=upper_threshold,
        min_threshold=lower_threshold,
        visualize_result=save_result
    )
