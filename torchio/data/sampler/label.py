from typing import Generator
from .sampler import ImageSampler, crop
from ... import DATA, LABEL
from ...utils import is_image_dict


class LabelSampler(ImageSampler):
    """
    This iterable dataset yields patches that contain at least one voxel
    without background.

    For now, this implementation is not efficient because it uses brute force
    to look for foreground voxels.

    It extracts the label data from the first image in the sample with type
    :py:attr:`torchio.LABEL`.
    """
    # pylint: disable=abstract-method
    def extract_patch_generator(
            self,
            sample: dict,
            patch_size,
            ) -> Generator[dict, None, None]:
        while True:
            yield self.extract_patch(sample, patch_size)

    @staticmethod
    def get_first_label_image_dict(sample: dict):
        for image_dict in sample.values():
            if not is_image_dict(image_dict):
                continue
            if image_dict['type'] == LABEL:
                label_image_dict = image_dict
                break
        else:
            raise ValueError('No images of type torchio.LABEL found in sample')
        return label_image_dict

    def extract_patch(self, sample: dict, patch_size):
        has_label = False
        label_image_data = self.get_first_label_image_dict(sample)[DATA]
        while not has_label:
            index_ini, index_fin = self.get_random_indices(sample, patch_size)
            patch_label = crop(label_image_data, index_ini, index_fin)
            has_label = patch_label.sum() > 0
        cropped_sample = self.copy_and_crop(
            sample,
            index_ini,
            index_fin,
        )
        return cropped_sample
