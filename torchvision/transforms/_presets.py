"""
This file is part of the private API. Please do not use directly these classes as they will be modified on
future versions without warning. The classes should be accessed only via the transforms argument of Weights.
"""
from typing import Dict, Optional, Tuple

import torch
from torch import Tensor, nn

from . import functional as F, InterpolationMode


__all__ = [
    "ObjectDetectionEval",
    "ImageClassificationEval",
    "VideoClassificationEval",
    "SemanticSegmentationEval",
    "OpticalFlowEval",
]


class ObjectDetectionEval(nn.Module):
    def forward(self, img: Tensor) -> Tensor:
        if not isinstance(img, Tensor):
            img = F.pil_to_tensor(img)
        return F.convert_image_dtype(img, torch.float)


class ImageClassificationEval(nn.Module):
    def __init__(
        self,
        crop_size: int,
        resize_size: int = 256,
        mean: Tuple[float, ...] = (0.485, 0.456, 0.406),
        std: Tuple[float, ...] = (0.229, 0.224, 0.225),
        interpolation: InterpolationMode = InterpolationMode.BILINEAR,
    ) -> None:
        super().__init__()
        self._crop_size = [crop_size]
        self._size = [resize_size]
        self._mean = list(mean)
        self._std = list(std)
        self._interpolation = interpolation

    def forward(self, img: Tensor) -> Tensor:
        img = F.resize(img, self._size, interpolation=self._interpolation)
        img = F.center_crop(img, self._crop_size)
        if not isinstance(img, Tensor):
            img = F.pil_to_tensor(img)
        img = F.convert_image_dtype(img, torch.float)
        img = F.normalize(img, mean=self._mean, std=self._std)
        return img


class VideoClassificationEval(nn.Module):
    def __init__(
        self,
        crop_size: Tuple[int, int],
        resize_size: Tuple[int, int],
        mean: Tuple[float, ...] = (0.43216, 0.394666, 0.37645),
        std: Tuple[float, ...] = (0.22803, 0.22145, 0.216989),
        interpolation: InterpolationMode = InterpolationMode.BILINEAR,
    ) -> None:
        super().__init__()
        self._crop_size = list(crop_size)
        self._size = list(resize_size)
        self._mean = list(mean)
        self._std = list(std)
        self._interpolation = interpolation

    def forward(self, vid: Tensor) -> Tensor:
        vid = vid.permute(0, 3, 1, 2)  # (T, H, W, C) => (T, C, H, W)
        vid = F.resize(vid, self._size, interpolation=self._interpolation)
        vid = F.center_crop(vid, self._crop_size)
        vid = F.convert_image_dtype(vid, torch.float)
        vid = F.normalize(vid, mean=self._mean, std=self._std)
        return vid.permute(1, 0, 2, 3)  # (T, C, H, W) => (C, T, H, W)


class SemanticSegmentationEval(nn.Module):
    def __init__(
        self,
        resize_size: Optional[int],
        mean: Tuple[float, ...] = (0.485, 0.456, 0.406),
        std: Tuple[float, ...] = (0.229, 0.224, 0.225),
        interpolation: InterpolationMode = InterpolationMode.BILINEAR,
        interpolation_target: InterpolationMode = InterpolationMode.NEAREST,
    ) -> None:
        super().__init__()
        self._size = [resize_size] if resize_size is not None else None
        self._mean = list(mean)
        self._std = list(std)
        self._interpolation = interpolation
        self._interpolation_target = interpolation_target

    def forward(self, img: Tensor) -> Tensor:
        if isinstance(self._size, list):
            img = F.resize(img, self._size, interpolation=self._interpolation)
        if not isinstance(img, Tensor):
            img = F.pil_to_tensor(img)
        img = F.convert_image_dtype(img, torch.float)
        img = F.normalize(img, mean=self._mean, std=self._std)
        return img


class OpticalFlowEval(nn.Module):
    def forward(self, img1: Tensor, img2: Tensor) -> Tuple[Tensor, Tensor]:
        if not isinstance(img1, Tensor):
            img1 = F.pil_to_tensor(img1)
        if not isinstance(img2, Tensor):
            img2 = F.pil_to_tensor(img2)

        img1 = F.convert_image_dtype(img1, torch.float32)
        img2 = F.convert_image_dtype(img2, torch.float32)

        # map [0, 1] into [-1, 1]
        img1 = F.normalize(img1, mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        img2 = F.normalize(img2, mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])

        img1 = img1.contiguous()
        img2 = img2.contiguous()

        return img1, img2
