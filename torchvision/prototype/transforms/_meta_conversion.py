from typing import Union, Any, Dict

import torch
import torchvision.prototype.transforms.kernels as K
from torchvision.prototype import features
from torchvision.prototype.transforms import Transform
from torchvision.transforms.functional import convert_image_dtype


class ConvertBoundingBoxFormat(Transform):
    def __init__(self, format: Union[str, features.BoundingBoxFormat]) -> None:
        super().__init__()
        if isinstance(format, str):
            format = features.BoundingBoxFormat[format]
        self.format = format

    def _transform(self, input: Any, params: Dict[str, Any]) -> Any:
        if not isinstance(input, features.BoundingBox):
            return input

        output = K.convert_bounding_box_format(input, old_format=input.format, new_format=self.format)
        return features.BoundingBox.new_like(input, output, format=self.format)


class ConvertImageDtype(Transform):
    def __init__(self, dtype: torch.dtype = torch.float32) -> None:
        super().__init__()
        self.dtype = dtype

    def _transform(self, input: Any, params: Dict[str, Any]) -> Any:
        if not isinstance(input, features.Image):
            return input

        output = convert_image_dtype(input, dtype=self.dtype)
        return features.Image.new_like(input, output, dtype=self.dtype)


class ConvertColorSpace(Transform):
    def __init__(self, color_space: Union[str, features.ColorSpace]) -> None:
        super().__init__()
        if isinstance(color_space, str):
            color_space = features.ColorSpace[color_space]
        self.color_space = color_space

    def _transform(self, input: Any, params: Dict[str, Any]) -> Any:
        if not isinstance(input, features.Image):
            return input

        output = K.convert_color_space(input, old_color_space=input.color_space, new_color_space=self.color_space)
        return features.Image.new_like(input, output, color_space=self.color_space)
