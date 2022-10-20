"""Run smoke tests"""

import torchvision
import torchvision._internally_replaced_utils  # noqa: F401
import torchvision._utils  # noqa: F401
import torchvision.datasets  # noqa: F401
import torchvision.datasets._optical_flow  # noqa: F401
import torchvision.datasets._stereo_matching  # noqa: F401
import torchvision.datasets.caltech  # noqa: F401
import torchvision.datasets.celeba  # noqa: F401
import torchvision.datasets.cifar  # noqa: F401
import torchvision.datasets.cityscapes  # noqa: F401
import torchvision.datasets.clevr  # noqa: F401
import torchvision.datasets.coco  # noqa: F401
import torchvision.datasets.country211  # noqa: F401
import torchvision.datasets.dtd  # noqa: F401
import torchvision.datasets.eurosat  # noqa: F401
import torchvision.datasets.fakedata  # noqa: F401
import torchvision.datasets.fer2013  # noqa: F401
import torchvision.datasets.fgvc_aircraft  # noqa: F401
import torchvision.datasets.flickr  # noqa: F401
import torchvision.datasets.flowers102  # noqa: F401
import torchvision.datasets.folder  # noqa: F401
import torchvision.datasets.food101  # noqa: F401
import torchvision.datasets.gtsrb  # noqa: F401
import torchvision.datasets.hmdb51  # noqa: F401
import torchvision.datasets.imagenet  # noqa: F401
import torchvision.datasets.inaturalist  # noqa: F401
import torchvision.datasets.kinetics  # noqa: F401
import torchvision.datasets.kitti  # noqa: F401
import torchvision.datasets.lfw  # noqa: F401
import torchvision.datasets.lsun  # noqa: F401
import torchvision.datasets.mnist  # noqa: F401
import torchvision.datasets.omniglot  # noqa: F401
import torchvision.datasets.oxford_iiit_pet  # noqa: F401
import torchvision.datasets.pcam  # noqa: F401
import torchvision.datasets.phototour  # noqa: F401
import torchvision.datasets.places365  # noqa: F401
import torchvision.datasets.rendered_sst2  # noqa: F401
import torchvision.datasets.sbd  # noqa: F401
import torchvision.datasets.sbu  # noqa: F401
import torchvision.datasets.semeion  # noqa: F401
import torchvision.datasets.stanford_cars  # noqa: F401
import torchvision.datasets.stl10  # noqa: F401
import torchvision.datasets.sun397  # noqa: F401
import torchvision.datasets.svhn  # noqa: F401
import torchvision.datasets.ucf101  # noqa: F401
import torchvision.datasets.usps  # noqa: F401
import torchvision.datasets.utils  # noqa: F401
import torchvision.datasets.video_utils  # noqa: F401
import torchvision.datasets.vision  # noqa: F401
import torchvision.datasets.voc  # noqa: F401
import torchvision.datasets.widerface  # noqa: F401
import torchvision.extension  # noqa: F401
import torchvision.io  # noqa: F401
import torchvision.io._load_gpu_decoder  # noqa: F401
import torchvision.io._video_opt  # noqa: F401
import torchvision.io.image  # noqa: F401
import torchvision.io.video  # noqa: F401
import torchvision.io.video_reader  # noqa: F401
import torchvision.models  # noqa: F401
import torchvision.models._api  # noqa: F401
import torchvision.models._meta  # noqa: F401
import torchvision.models._utils  # noqa: F401
import torchvision.models.alexnet  # noqa: F401
import torchvision.models.convnext  # noqa: F401
import torchvision.models.densenet  # noqa: F401
import torchvision.models.detection  # noqa: F401
import torchvision.models.detection._utils  # noqa: F401
import torchvision.models.detection.anchor_utils  # noqa: F401
import torchvision.models.detection.backbone_utils  # noqa: F401
import torchvision.models.detection.faster_rcnn  # noqa: F401
import torchvision.models.detection.fcos  # noqa: F401
import torchvision.models.detection.generalized_rcnn  # noqa: F401
import torchvision.models.detection.image_list  # noqa: F401
import torchvision.models.detection.keypoint_rcnn  # noqa: F401
import torchvision.models.detection.mask_rcnn  # noqa: F401
import torchvision.models.detection.retinanet  # noqa: F401
import torchvision.models.detection.roi_heads  # noqa: F401
import torchvision.models.detection.rpn  # noqa: F401
import torchvision.models.detection.ssd  # noqa: F401
import torchvision.models.detection.ssdlite  # noqa: F401
import torchvision.models.detection.transform  # noqa: F401
import torchvision.models.efficientnet  # noqa: F401
import torchvision.models.googlenet  # noqa: F401
import torchvision.models.inception  # noqa: F401
import torchvision.models.maxvit  # noqa: F401
import torchvision.models.mnasnet  # noqa: F401
import torchvision.models.mobilenet  # noqa: F401
import torchvision.models.mobilenetv2  # noqa: F401
import torchvision.models.mobilenetv3  # noqa: F401
import torchvision.models.optical_flow  # noqa: F401
import torchvision.models.optical_flow._utils  # noqa: F401
import torchvision.models.optical_flow.raft  # noqa: F401
import torchvision.models.quantization  # noqa: F401
import torchvision.models.quantization.googlenet  # noqa: F401
import torchvision.models.quantization.inception  # noqa: F401
import torchvision.models.quantization.mobilenet  # noqa: F401
import torchvision.models.quantization.mobilenetv2  # noqa: F401
import torchvision.models.quantization.mobilenetv3  # noqa: F401
import torchvision.models.quantization.resnet  # noqa: F401
import torchvision.models.quantization.shufflenetv2  # noqa: F401
import torchvision.models.quantization.utils  # noqa: F401
import torchvision.models.regnet  # noqa: F401
import torchvision.models.resnet  # noqa: F401
import torchvision.models.segmentation  # noqa: F401
import torchvision.models.segmentation._utils  # noqa: F401
import torchvision.models.segmentation.deeplabv3  # noqa: F401
import torchvision.models.segmentation.fcn  # noqa: F401
import torchvision.models.segmentation.lraspp  # noqa: F401
import torchvision.models.shufflenetv2  # noqa: F401
import torchvision.models.squeezenet  # noqa: F401
import torchvision.models.swin_transformer  # noqa: F401
import torchvision.models.vgg  # noqa: F401
import torchvision.models.video  # noqa: F401
import torchvision.models.video.mvit  # noqa: F401
import torchvision.models.video.resnet  # noqa: F401
import torchvision.models.video.s3d  # noqa: F401
import torchvision.models.vision_transformer  # noqa: F401
import torchvision.ops  # noqa: F401
import torchvision.ops._box_convert  # noqa: F401
import torchvision.ops._register_onnx_ops  # noqa: F401
import torchvision.ops._utils  # noqa: F401
import torchvision.ops.boxes  # noqa: F401
import torchvision.ops.ciou_loss  # noqa: F401
import torchvision.ops.deform_conv  # noqa: F401
import torchvision.ops.diou_loss  # noqa: F401
import torchvision.ops.drop_block  # noqa: F401
import torchvision.ops.feature_pyramid_network  # noqa: F401
import torchvision.ops.focal_loss  # noqa: F401
import torchvision.ops.giou_loss  # noqa: F401
import torchvision.ops.misc  # noqa: F401
import torchvision.ops.poolers  # noqa: F401
import torchvision.ops.ps_roi_align  # noqa: F401
import torchvision.ops.ps_roi_pool  # noqa: F401
import torchvision.ops.roi_align  # noqa: F401
import torchvision.ops.roi_pool  # noqa: F401
import torchvision.ops.stochastic_depth  # noqa: F401
import torchvision.transforms  # noqa: F401
import torchvision.transforms._pil_constants  # noqa: F401
import torchvision.transforms._presets  # noqa: F401
import torchvision.transforms.autoaugment  # noqa: F401
import torchvision.transforms.functional  # noqa: F401
import torchvision.transforms.functional_pil  # noqa: F401
import torchvision.transforms.functional_tensor  # noqa: F401
import torchvision.transforms.transforms  # noqa: F401
import torchvision.utils  # noqa: F401
import torchvision.version  # noqa: F401

print("torchvision version is ", torchvision.__version__)
