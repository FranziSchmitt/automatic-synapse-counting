from pathlib import Path
from typing import List

from pims import ImageSequence
from skimage.color import rgb2grey


class DataLoader(object):
    def __init__(self, filepath: Path, sequence_adjust_params: dict):
        self.images = None
        self.final_images = list()
        self.meta_data = dict()
        self.load_data(filepath)
        self.cropped_images = list()

        y_start = sequence_adjust_params["y_start"]
        x_start = sequence_adjust_params["x_start"]
        lower_threshold = sequence_adjust_params["lower_threshold"]
        upper_threshold = sequence_adjust_params["upper_threshold"]
        square_size = sequence_adjust_params["square_size"]
        self.adjust_sequence(
            y_start=y_start,
            x_start=x_start,
            lower_threshold=lower_threshold,
            upper_threshold=upper_threshold,
            square_size=square_size,
        )

    def load_data(self, filepath: Path) -> None:
        paths = Path(filepath)
        image_paths = [i for i in paths.iterdir() if ".tif" in str(i)]
        meta_data_path = [i for i in paths.iterdir() if ".txt" in str(i)][0]

        images = ImageSequence(image_paths, as_grey=True)
        self.images = self.grey_sequence(images)

        with open(str(meta_data_path), "r", encoding="latin-1") as fid:
            text_file = fid.readlines()

        for line in text_file:
            if "Voxel-Height" in line.split():
                self.meta_data["voxel_size"] = float(line.split()[-1][:-1])
            elif "Voxel_Depth" in line.split():
                self.meta_data["voxel_depth"] = float(line.split()[-1][:-1])

    @staticmethod
    def grey_sequence(rgb_sequence: ImageSequence) -> List[ImageSequence]:

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
        square_size: int,
    ) -> None:
        pixel_number = square_size / self.meta_data["voxel_size"]

        y_stop = int(y_start + pixel_number)
        x_stop = int(x_start + pixel_number)

        self.cropped_images = [i[y_start:y_stop, x_start:x_stop] for i in self.images]

        for im in self.cropped_images:
            image = im.copy()
            image[image < lower_threshold] = 0
            image[image > upper_threshold] = 100000
            self.final_images.append(image)
