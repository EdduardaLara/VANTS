import os.path

import PIL.Image
import numpy
import pytest
import torch

import torchvision.ops

ASSETS_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


@pytest.fixture
def labeled_image() -> torch.Tensor:
    with PIL.Image.open(os.path.join(ASSETS_DIRECTORY, "labeled_image.png")) as image:
        return torch.tensor(numpy.array(image, numpy.int))


@pytest.fixture
def masks() -> torch.Tensor:
    with PIL.Image.open(os.path.join(ASSETS_DIRECTORY, "masks.tiff")) as image:
        frames = numpy.zeros((image.n_frames, image.height, image.width), numpy.int)

        for index in range(image.n_frames):
            image.seek(index)

            frames[index] = numpy.array(image)

        return torch.tensor(frames)


def test_masks_to_bounding_boxes(masks):
    expected = torch.tensor(
       [[ 127.,    2.,  165.,   40. ],  # noqa: E201, E202
        [   4.,  100.,   88.,  184. ],  # noqa: E201, E202
        [ 168.,  189.,  294.,  300. ],  # noqa: E201, E202
        [ 556.,  272.,  700.,  416. ],  # noqa: E201, E202
        [ 800.,  560.,  990.,  725. ],  # noqa: E201, E202
        [ 294.,  828.,  594., 1092. ],  # noqa: E201, E202
        [ 756., 1036., 1064., 1491. ]]  # noqa: E201, E202
    )

    torch.testing.assert_close(torchvision.ops.masks_to_bounding_boxes(masks), expected)
