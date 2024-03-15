from torchvision.transforms import InterpolationMode  # usort: skip

from ._utils import is_pure_tensor, register_kernel  # usort: skip

from ._meta import (
    clamp_bounding_boxes,
    convert_bounding_box_format,
    get_dimensions_image,
    _get_dimensions_image_pil,
    get_dimensions_video,
    get_dimensions,
    get_num_frames_video,
    get_num_frames,
    get_image_num_channels,
    get_num_channels_image,
    _get_num_channels_image_pil,
    get_num_channels_video,
    get_num_channels,
    get_size_bounding_boxes,
    get_size_image,
    _get_size_image_pil,
    get_size_mask,
    get_size_video,
    get_size,
)  # usort: skip

from ._augment import _erase_image_pil, _jpeg_image_pil, erase, erase_image, erase_video, jpeg, jpeg_image, jpeg_video
from ._color import (
    _adjust_brightness_image_pil,
    _adjust_contrast_image_pil,
    _adjust_gamma_image_pil,
    _adjust_hue_image_pil,
    _adjust_saturation_image_pil,
    _adjust_sharpness_image_pil,
    _autocontrast_image_pil,
    _equalize_image_pil,
    _invert_image_pil,
    _permute_channels_image_pil,
    _posterize_image_pil,
    _rgb_to_grayscale_image_pil,
    _solarize_image_pil,
    adjust_brightness,
    adjust_brightness_image,
    adjust_brightness_video,
    adjust_contrast,
    adjust_contrast_image,
    adjust_contrast_video,
    adjust_gamma,
    adjust_gamma_image,
    adjust_gamma_video,
    adjust_hue,
    adjust_hue_image,
    adjust_hue_video,
    adjust_saturation,
    adjust_saturation_image,
    adjust_saturation_video,
    adjust_sharpness,
    adjust_sharpness_image,
    adjust_sharpness_video,
    autocontrast,
    autocontrast_image,
    autocontrast_video,
    equalize,
    equalize_image,
    equalize_video,
    invert,
    invert_image,
    invert_video,
    permute_channels,
    permute_channels_image,
    permute_channels_video,
    posterize,
    posterize_image,
    posterize_video,
    rgb_to_grayscale,
    rgb_to_grayscale_image,
    solarize,
    solarize_image,
    solarize_video,
    to_grayscale,
)
from ._geometry import (
    _affine_image_pil,
    _center_crop_image_pil,
    _crop_image_pil,
    _elastic_image_pil,
    _five_crop_image_pil,
    _horizontal_flip_image_pil,
    _pad_image_pil,
    _perspective_image_pil,
    _resize_image_pil,
    _resized_crop_image_pil,
    _rotate_image_pil,
    _ten_crop_image_pil,
    _vertical_flip_image_pil,
    affine,
    affine_bounding_boxes,
    affine_image,
    affine_mask,
    affine_video,
    center_crop,
    center_crop_bounding_boxes,
    center_crop_image,
    center_crop_mask,
    center_crop_video,
    crop,
    crop_bounding_boxes,
    crop_image,
    crop_mask,
    crop_video,
    elastic,
    elastic_bounding_boxes,
    elastic_image,
    elastic_mask,
    elastic_transform,
    elastic_video,
    five_crop,
    five_crop_image,
    five_crop_video,
    hflip,  # TODO: Consider moving all pure alias definitions at the bottom of the file
    horizontal_flip,
    horizontal_flip_bounding_boxes,
    horizontal_flip_image,
    horizontal_flip_mask,
    horizontal_flip_video,
    pad,
    pad_bounding_boxes,
    pad_image,
    pad_mask,
    pad_video,
    perspective,
    perspective_bounding_boxes,
    perspective_image,
    perspective_mask,
    perspective_video,
    resize,
    resize_bounding_boxes,
    resize_image,
    resize_mask,
    resize_video,
    resized_crop,
    resized_crop_bounding_boxes,
    resized_crop_image,
    resized_crop_mask,
    resized_crop_video,
    rotate,
    rotate_bounding_boxes,
    rotate_image,
    rotate_mask,
    rotate_video,
    ten_crop,
    ten_crop_image,
    ten_crop_video,
    vertical_flip,
    vertical_flip_bounding_boxes,
    vertical_flip_image,
    vertical_flip_mask,
    vertical_flip_video,
    vflip,
)
from ._misc import (
    _gaussian_blur_image_pil,
    convert_image_dtype,
    gaussian_blur,
    gaussian_blur_image,
    gaussian_blur_video,
    normalize,
    normalize_image,
    normalize_video,
    sanitize_bounding_boxes,
    to_dtype,
    to_dtype_image,
    to_dtype_video,
)
from ._temporal import uniform_temporal_subsample, uniform_temporal_subsample_video
from ._type_conversion import pil_to_tensor, to_image, to_pil_image

from ._deprecated import get_image_size, to_tensor  # usort: skip
