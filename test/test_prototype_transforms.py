import itertools

import pytest
import torch
from common_utils import assert_equal
from test_prototype_transforms_functional import make_images, make_bounding_boxes, make_one_hot_labels
from torchvision.prototype import transforms, features
from torchvision.transforms.functional import to_pil_image, pil_to_tensor


def make_vanilla_tensor_images(*args, **kwargs):
    for image in make_images(*args, **kwargs):
        if image.ndim > 3:
            continue
        yield image.data


def make_pil_images(*args, **kwargs):
    for image in make_vanilla_tensor_images(*args, **kwargs):
        yield to_pil_image(image)


def make_vanilla_tensor_bounding_boxes(*args, **kwargs):
    for bounding_box in make_bounding_boxes(*args, **kwargs):
        yield bounding_box.data


def parametrize(transforms_with_inputs):
    return pytest.mark.parametrize(
        ("transform", "input"),
        [
            pytest.param(
                transform,
                input,
                id=f"{type(transform).__name__}-{type(input).__module__}.{type(input).__name__}-{idx}",
            )
            for transform, inputs in transforms_with_inputs
            for idx, input in enumerate(inputs)
        ],
    )


def parametrize_from_transforms(*transforms):
    transforms_with_inputs = []
    for transform in transforms:
        for creation_fn in [
            make_images,
            make_bounding_boxes,
            make_one_hot_labels,
            make_vanilla_tensor_images,
            make_pil_images,
        ]:
            inputs = list(creation_fn())
            try:
                output = transform(inputs[0])
            except Exception:
                continue
            else:
                if output is inputs[0]:
                    continue

            transforms_with_inputs.append((transform, inputs))

    return parametrize(transforms_with_inputs)


class TestSmoke:
    @parametrize_from_transforms(
        transforms.RandomErasing(p=1.0),
        transforms.Resize([16, 16]),
        transforms.CenterCrop([16, 16]),
        transforms.ConvertImageDtype(),
        transforms.RandomHorizontalFlip(),
    )
    def test_common(self, transform, input):
        transform(input)

    @parametrize(
        [
            (
                transform,
                [
                    dict(
                        image=features.Image.new_like(image, image.unsqueeze(0), dtype=torch.float),
                        one_hot_label=features.OneHotLabel.new_like(
                            one_hot_label, one_hot_label.unsqueeze(0), dtype=torch.float
                        ),
                    )
                    for image, one_hot_label in itertools.product(make_images(), make_one_hot_labels())
                ],
            )
            for transform in [
                transforms.RandomMixup(alpha=1.0),
                transforms.RandomCutmix(alpha=1.0),
            ]
        ]
    )
    def test_mixup_cutmix(self, transform, input):
        transform(input)

    @parametrize(
        [
            (
                transform,
                itertools.chain.from_iterable(
                    fn(dtypes=[torch.uint8], extra_dims=[(4,)])
                    for fn in [
                        make_images,
                        make_vanilla_tensor_images,
                        make_pil_images,
                    ]
                ),
            )
            for transform in (
                transforms.RandAugment(),
                transforms.TrivialAugmentWide(),
                transforms.AutoAugment(),
                transforms.AugMix(),
            )
        ]
    )
    def test_auto_augment(self, transform, input):
        transform(input)

    @parametrize(
        [
            (
                transforms.Normalize(mean=[0.0, 0.0, 0.0], std=[1.0, 1.0, 1.0]),
                itertools.chain.from_iterable(
                    fn(color_spaces=[features.ColorSpace.RGB], dtypes=[torch.float32])
                    for fn in [
                        make_images,
                        make_vanilla_tensor_images,
                    ]
                ),
            ),
        ]
    )
    def test_normalize(self, transform, input):
        transform(input)

    @parametrize(
        [
            (
                transforms.RandomResizedCrop([16, 16]),
                itertools.chain(
                    make_images(extra_dims=[(4,)]),
                    make_vanilla_tensor_images(),
                    make_pil_images(),
                ),
            )
        ]
    )
    def test_random_resized_crop(self, transform, input):
        transform(input)


class TestRandomHorizontalFlip:
    def input_tensor(self, dtype=torch.float32):
        return torch.tensor([[[0, 1], [0, 1]], [[1, 0], [1, 0]]], dtype=dtype)

    def expected_tensor(self, dtype=torch.float32):
        return torch.tensor([[[1, 0], [1, 0]], [[0, 1], [0, 1]]], dtype=dtype)

    @pytest.mark.parametrize("p", [0.0, 1.0], ids=["p=0", "p=1"])
    def test_simple_tensor(self, p):
        input = self.input_tensor()

        actual = transforms.RandomHorizontalFlip(p=p)(input)

        expected = self.expected_tensor() if p == 1.0 else input
        assert_equal(expected, actual)

    @pytest.mark.parametrize("p", [0.0, 1.0], ids=["p=0", "p=1"])
    def test_pil_image(self, p):
        input = self.input_tensor(dtype=torch.uint8)

        actual = transforms.RandomHorizontalFlip(p=p)(to_pil_image(input))

        expected = self.expected_tensor(dtype=torch.uint8) if p == 1.0 else input
        assert_equal(expected, pil_to_tensor(actual))

    @pytest.mark.parametrize("p", [0.0, 1.0], ids=["p=0", "p=1"])
    def test_features_image(self, p):
        input = self.input_tensor()

        actual = transforms.RandomHorizontalFlip(p=p)(features.Image(input))

        expected = self.expected_tensor() if p == 1.0 else input
        assert_equal(features.Image(expected), actual)

    @pytest.mark.parametrize("p", [0.0, 1.0], ids=["p=0", "p=1"])
    def test_features_segmentation_mask(self, p):
        input = features.SegmentationMask(self.input_tensor())

        actual = transforms.RandomHorizontalFlip(p=p)(input)

        expected = self.expected_tensor() if p == 1.0 else input
        assert_equal(features.SegmentationMask(expected), actual)

    @pytest.mark.parametrize("p", [0.0, 1.0], ids=["p=0", "p=1"])
    def test_features_bounding_box(self, p):
        input = features.BoundingBox([0, 0, 5, 5], format=features.BoundingBoxFormat.XYXY, image_size=(10, 10))

        actual = transforms.RandomHorizontalFlip(p=p)(input)

        expected = torch.tensor([5, 0, 10, 5]) if p == 1.0 else input
        assert_equal(features.BoundingBox.new_like(input, expected), actual)
