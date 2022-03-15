import importlib
import os

import pytest
import test_models as TM
import torch
import torchvision
from common_utils import cpu_and_gpu, needs_cuda
from torchvision.models._api import WeightsEnum, Weights
from torchvision.models._utils import handle_legacy_interface
from torchvision.prototype import models

run_if_test_with_prototype = pytest.mark.skipif(
    os.getenv("PYTORCH_TEST_WITH_PROTOTYPE") != "1",
    reason="Prototype tests are disabled by default. Set PYTORCH_TEST_WITH_PROTOTYPE=1 to run them.",
)


def _get_original_model(model_fn):
    original_module_name = model_fn.__module__.replace(".prototype", "")
    module = importlib.import_module(original_module_name)
    return module.__dict__[model_fn.__name__]


def _get_parent_module(model_fn):
    parent_module_name = ".".join(model_fn.__module__.split(".")[:-1])
    module = importlib.import_module(parent_module_name)
    return module


def _get_model_weights(model_fn):
    module = _get_parent_module(model_fn)
    weights_name = "_QuantizedWeights" if module.__name__.split(".")[-1] == "quantization" else "_Weights"
    try:
        return next(
            v
            for k, v in module.__dict__.items()
            if k.endswith(weights_name) and k.replace(weights_name, "").lower() == model_fn.__name__
        )
    except StopIteration:
        return None


def _build_model(fn, **kwargs):
    try:
        model = fn(**kwargs)
    except ValueError as e:
        msg = str(e)
        if "No checkpoint is available" in msg:
            pytest.skip(msg)
        raise e
    return model.eval()


@pytest.mark.parametrize(
    "name, weight",
    [
        ("ResNet50_Weights.IMAGENET1K_V1", torchvision.models.ResNet50_Weights.IMAGENET1K_V1),
        ("ResNet50_Weights.DEFAULT", torchvision.models.ResNet50_Weights.IMAGENET1K_V2),
        (
            "ResNet50_QuantizedWeights.DEFAULT",
            torchvision.models.quantization.ResNet50_QuantizedWeights.IMAGENET1K_FBGEMM_V2,
        ),
        (
            "ResNet50_QuantizedWeights.IMAGENET1K_FBGEMM_V1",
            torchvision.models.quantization.ResNet50_QuantizedWeights.IMAGENET1K_FBGEMM_V1,
        ),
    ],
)
def test_get_weight(name, weight):
    assert torchvision.models.get_weight(name) == weight


@pytest.mark.parametrize(
    "model_fn",
    TM.get_models_from_module(torchvision.models)
    + TM.get_models_from_module(torchvision.models.detection)
    + TM.get_models_from_module(torchvision.models.quantization)
    + TM.get_models_from_module(models.segmentation)
    + TM.get_models_from_module(models.video)
    + TM.get_models_from_module(models.optical_flow),
)
def test_naming_conventions(model_fn):
    weights_enum = _get_model_weights(model_fn)
    print(weights_enum)
    assert weights_enum is not None
    assert len(weights_enum) == 0 or hasattr(weights_enum, "DEFAULT")


@pytest.mark.parametrize(
    "model_fn",
    TM.get_models_from_module(torchvision.models)
    + TM.get_models_from_module(torchvision.models.detection)
    + TM.get_models_from_module(torchvision.models.quantization)
    + TM.get_models_from_module(models.segmentation)
    + TM.get_models_from_module(models.video)
    + TM.get_models_from_module(models.optical_flow),
)
@run_if_test_with_prototype
def test_schema_meta_validation(model_fn):
    classification_fields = ["size", "categories", "acc@1", "acc@5", "min_size"]
    defaults = {
        "all": ["task", "architecture", "publication_year", "interpolation", "recipe", "num_params"],
        "models": classification_fields,
        "detection": ["categories", "map"],
        "quantization": classification_fields + ["backend", "quantization", "unquantized"],
        "segmentation": ["categories", "mIoU", "acc"],
        "video": classification_fields,
        "optical_flow": [],
    }
    model_name = model_fn.__name__
    module_name = model_fn.__module__.split(".")[-2]
    fields = set(defaults["all"] + defaults[module_name])

    weights_enum = _get_model_weights(model_fn)
    if len(weights_enum) == 0:
        pytest.skip(f"Model '{model_name}' doesn't have any pre-trained weights.")

    problematic_weights = {}
    incorrect_params = []
    bad_names = []
    for w in weights_enum:
        missing_fields = fields - set(w.meta.keys())
        if missing_fields:
            problematic_weights[w] = missing_fields
        if w == weights_enum.DEFAULT:
            if module_name == "quantization":
                # parameters() count doesn't work well with quantization, so we check against the non-quantized
                unquantized_w = w.meta.get("unquantized")
                if unquantized_w is not None and w.meta.get("num_params") != unquantized_w.meta.get("num_params"):
                    incorrect_params.append(w)
            else:
                if w.meta.get("num_params") != sum(p.numel() for p in model_fn(weights=w).parameters()):
                    incorrect_params.append(w)
        else:
            if w.meta.get("num_params") != weights_enum.DEFAULT.meta.get("num_params"):
                incorrect_params.append(w)
        if not w.name.isupper():
            bad_names.append(w)

    assert not problematic_weights
    assert not incorrect_params
    assert not bad_names


@pytest.mark.parametrize("model_fn", TM.get_models_from_module(models.segmentation))
@pytest.mark.parametrize("dev", cpu_and_gpu())
@run_if_test_with_prototype
def test_segmentation_model(model_fn, dev):
    TM.test_segmentation_model(model_fn, dev)


@pytest.mark.parametrize("model_fn", TM.get_models_from_module(models.video))
@pytest.mark.parametrize("dev", cpu_and_gpu())
@run_if_test_with_prototype
def test_video_model(model_fn, dev):
    TM.test_video_model(model_fn, dev)


@needs_cuda
@pytest.mark.parametrize("model_builder", TM.get_models_from_module(models.optical_flow))
@pytest.mark.parametrize("scripted", (False, True))
@run_if_test_with_prototype
def test_raft(model_builder, scripted):
    TM.test_raft(model_builder, scripted)


@pytest.mark.parametrize(
    "model_fn",
    TM.get_models_from_module(models.segmentation)
    + TM.get_models_from_module(models.video)
    + TM.get_models_from_module(models.optical_flow),
)
@pytest.mark.parametrize("dev", cpu_and_gpu())
@run_if_test_with_prototype
def test_old_vs_new_factory(model_fn, dev):
    defaults = {
        "models": {
            "input_shape": (1, 3, 224, 224),
        },
        "detection": {
            "input_shape": (3, 300, 300),
        },
        "quantization": {
            "input_shape": (1, 3, 224, 224),
            "quantize": True,
        },
        "segmentation": {
            "input_shape": (1, 3, 520, 520),
        },
        "video": {
            "input_shape": (1, 3, 4, 112, 112),
        },
        "optical_flow": {
            "input_shape": (1, 3, 128, 128),
        },
    }
    model_name = model_fn.__name__
    module_name = model_fn.__module__.split(".")[-2]
    kwargs = {"pretrained": True, **defaults[module_name], **TM._model_params.get(model_name, {})}
    input_shape = kwargs.pop("input_shape")
    kwargs.pop("num_classes", None)  # ignore this as it's an incompatible speed optimization for pre-trained models
    x = torch.rand(input_shape).to(device=dev)
    if module_name == "detection":
        x = [x]

    if module_name == "optical_flow":
        args = [x, x]  # RAFT model requires img1, img2 as input
    else:
        args = [x]

    # compare with new model builder parameterized in the old fashion way
    try:
        model_old = _build_model(_get_original_model(model_fn), **kwargs).to(device=dev)
        model_new = _build_model(model_fn, **kwargs).to(device=dev)
    except ModuleNotFoundError:
        pytest.skip(f"Model '{model_name}' not available in both modules.")
    torch.testing.assert_close(model_new(*args), model_old(*args), rtol=0.0, atol=0.0, check_dtype=False)


def test_smoke():
    import torchvision.prototype.models  # noqa: F401


# With this filter, every unexpected warning will be turned into an error
@pytest.mark.filterwarnings("error")
class TestHandleLegacyInterface:
    class ModelWeights(WeightsEnum):
        Sentinel = Weights(url="https://pytorch.org", transforms=lambda x: x, meta=dict())

    @pytest.mark.parametrize(
        "kwargs",
        [
            pytest.param(dict(), id="empty"),
            pytest.param(dict(weights=None), id="None"),
            pytest.param(dict(weights=ModelWeights.Sentinel), id="Weights"),
        ],
    )
    def test_no_warn(self, kwargs):
        @handle_legacy_interface(weights=("pretrained", self.ModelWeights.Sentinel))
        def builder(*, weights=None):
            pass

        builder(**kwargs)

    @pytest.mark.parametrize("pretrained", (True, False))
    def test_pretrained_pos(self, pretrained):
        @handle_legacy_interface(weights=("pretrained", self.ModelWeights.Sentinel))
        def builder(*, weights=None):
            pass

        with pytest.warns(UserWarning, match="positional"):
            builder(pretrained)

    @pytest.mark.parametrize("pretrained", (True, False))
    def test_pretrained_kw(self, pretrained):
        @handle_legacy_interface(weights=("pretrained", self.ModelWeights.Sentinel))
        def builder(*, weights=None):
            pass

        with pytest.warns(UserWarning, match="deprecated"):
            builder(pretrained)

    @pytest.mark.parametrize("pretrained", (True, False))
    @pytest.mark.parametrize("positional", (True, False))
    def test_equivalent_behavior_weights(self, pretrained, positional):
        @handle_legacy_interface(weights=("pretrained", self.ModelWeights.Sentinel))
        def builder(*, weights=None):
            pass

        args, kwargs = ((pretrained,), dict()) if positional else ((), dict(pretrained=pretrained))
        with pytest.warns(UserWarning, match=f"weights={self.ModelWeights.Sentinel if pretrained else None}"):
            builder(*args, **kwargs)

    def test_multi_params(self):
        weights_params = ("weights", "weights_other")
        pretrained_params = [param.replace("weights", "pretrained") for param in weights_params]

        @handle_legacy_interface(
            **{
                weights_param: (pretrained_param, self.ModelWeights.Sentinel)
                for weights_param, pretrained_param in zip(weights_params, pretrained_params)
            }
        )
        def builder(*, weights=None, weights_other=None):
            pass

        for pretrained_param in pretrained_params:
            with pytest.warns(UserWarning, match="deprecated"):
                builder(**{pretrained_param: True})

    def test_default_callable(self):
        @handle_legacy_interface(
            weights=(
                "pretrained",
                lambda kwargs: self.ModelWeights.Sentinel if kwargs["flag"] else None,
            )
        )
        def builder(*, weights=None, flag):
            pass

        with pytest.warns(UserWarning, match="deprecated"):
            builder(pretrained=True, flag=True)

        with pytest.raises(ValueError, match="weights"):
            builder(pretrained=True, flag=False)
