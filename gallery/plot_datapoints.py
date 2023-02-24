"""
==============
Datapoints FAQ
==============

The :mod:`torchvision.datapoints` namespace was introduced to ``torchvision.transforms.v2``. This example showcases what
these datapoints are and how they behave.
"""

import PIL.Image

import torch
import torchvision

# We are using BETA APIs, so we deactivate the associated warning, thereby acknowledging that
# some APIs may slightly change in the future
torchvision.disable_beta_transforms_warning()

from torchvision import datapoints


########################################################################################################################
# What are datapoints?
# --------------------
#
# Datapoints are zero-copy tensor subclasses:

tensor = torch.rand(3, 256, 256)
image = datapoints.Image(tensor)

assert isinstance(image, torch.Tensor)
assert image.data_ptr() == tensor.data_ptr()


########################################################################################################################
# They are needed in :mod:`torchvision.transforms.v2` for the automatic dispatch to the correct kernel.
#
# What datapoints are supported?
# ------------------------------
#
# So far :mod:`torchvision.datapoints` supports four types of datapoints:
#
# * :class:`~torchvision.datapoints.Image`
# * :class:`~torchvision.datapoints.Video`
# * :class:`~torchvision.datapoints.BoundingBox`
# * :class:`~torchvision.datapoints.Mask`
#
# How do I construct a datapoint?
# -------------------------------
#
# Each datapoint class takes any tensor-like data that can be turned into a :class:`~torch.Tensor`

image = datapoints.Image([[0, 1], [1, 0]])
print(image)


########################################################################################################################
# Similar to other PyTorch creations ops, the constructor also takes the ``dtype``, ``device``, and ``requires_grad``
# parameters.

float_image = datapoints.Image([[0, 1], [1, 0]], dtype=torch.float32, requires_grad=True)
print(float_image)


########################################################################################################################
# In addition, :class:`~torchvision.datapoints.Image` and :class:`~torchvision.datapoints.Mask` also take a
# :class:`PIL.Image.Image` directly:

image = datapoints.Image(PIL.Image.open("assets/astronaut.jpg"))
print(image.shape, image.dtype)

########################################################################################################################
# In general, the datapoints can also store additional metadata that complements the underlying tensor. For example,
# :class:`~torchvision.datapoints.BoundingBox` stores the coordinates format as well as the spatial size of the corresponding image
# alongside the actual values:

bounding_box = datapoints.BoundingBox(
    [17, 16, 344, 495], format=datapoints.BoundingBoxFormat.XYXY, spatial_size=image.shape[-2:]
)
print(bounding_box)


########################################################################################################################
# Do I have to wrap the output of the datasets myself?
# ----------------------------------------------------
#
# Only if you are using custom datasets. For the built-in ones, you can use
# :func:`torchvision.datasets.wrap_dataset_for_transforms_v2`. Note that the function also supports subclasses of the
# built-in datasets. Meaning, if your custom dataset subclasses from a built-in one and the output type is the same, you
# also don't have to wrap manually.
#
# How do the datapoints behave inside a computation?
# --------------------------------------------------
#
# Datapoints look and feel just like regular tensors. Everything that is supported on plain :class:`torch.Tensor`'s
# also works on datapoints.
# Since for most operations involving datapoints, it cannot be safely inferred whether the result should retain the
# datapoint type, we choose to return a plain tensor instead of a datapoint (this might change, see note below):

assert type(image) is datapoints.Image

new_image = image + 0

assert type(new_image) is torch.Tensor

########################################################################################################################
# There are two exceptions to this rule:
#
# 1. The operations :meth:`~torch.Tensor.clone`, :meth:`~torch.Tensor.to`, and :meth:`~torch.Tensor.requires_grad_`
#    retain the datapoint type.
# 2. Inplace operations on datapoints cannot change the type of the datapoint they are called on. However, if you use
#    the flow style, the returned value will be unwrapped:

image = datapoints.Image([[0, 1], [1, 0]])

new_image = image.add_(1)

assert type(image) is datapoints.Image
print(image)

assert type(new_image) is torch.Tensor
assert (new_image == image).all()
