import io
import pathlib
from functools import partial
from typing import Any, Callable, Dict, List, Optional, Tuple

import torch
from torchdata.datapipes.iter import IterDataPipe, Mapper, Filter, CSVDictParser, Zipper
from torchvision.prototype.datasets.utils import (
    Dataset,
    DatasetConfig,
    DatasetInfo,
    OnlineResource,
    DatasetType,
    HttpResource,
)
from torchvision.prototype.datasets.utils._internal import (
    path_comparator,
    hint_sharding,
    hint_shuffling,
)
from torchvision.prototype.features import Label


class GTSRB(Dataset):
    def _make_info(self) -> DatasetInfo:
        return DatasetInfo(
            "gtsrb",
            type=DatasetType.IMAGE,
            homepage="https://benchmark.ini.rub.de",
            categories=[f"{label:05d}" for label in range(43)],
            valid_options=dict(split=("train", "test")),
        )

    _URL_ROOT = "https://sid.erda.dk/public/archives/daaeac0d7ce1152aea9b61d9f1e19370/"
    _URLS = {
        "train": f"{_URL_ROOT}GTSRB-Training_fixed.zip",
        "test": f"{_URL_ROOT}GTSRB_Final_Test_Images.zip",
        "test_ground_truth": f"{_URL_ROOT}GTSRB_Final_Test_GT.zip",
    }
    _CHECKSUMS = {
        "train": "df4144942083645bd60b594de348aa6930126c3e0e5de09e39611630abf8455a",
        "test": "48ba6fab7e877eb64eaf8de99035b0aaecfbc279bee23e35deca4ac1d0a837fa",
        "test_ground_truth": "f94e5a7614d75845c74c04ddb26b8796b9e483f43541dd95dd5b726504e16d6d",
    }

    def resources(self, config: DatasetConfig) -> List[OnlineResource]:
        rsrcs: List[OnlineResource] = [HttpResource(self._URLS[config.split], sha256=self._CHECKSUMS[config.split])]

        if config.split == "test":
            rsrcs.append(
                HttpResource(
                    self._URLS["test_ground_truth"],
                    sha256=self._CHECKSUMS["test_ground_truth"],
                )
            )

        return rsrcs

    def _append_label_train(self, path_and_handle: Tuple[str, Any]) -> Tuple[str, Any, int]:
        path, handle = path_and_handle
        label = int(pathlib.Path(path).parent.name)
        return path, handle, label

    def _append_label_test(self, data: Tuple[Tuple[str, Any], Dict[str, Any]]) -> Tuple[str, Any, int]:
        (path, handle), csv_info = data
        label = int(csv_info["ClassId"])
        return path, handle, label

    def _collate(
        self, data: Tuple[str, Any, int], decoder: Optional[Callable[[io.IOBase], torch.Tensor]]
    ) -> Dict[str, Any]:
        image_path, image_buffer, label = data
        return {
            "image_path": image_path,
            "image": decoder(image_buffer) if decoder else image_buffer,
            "label": Label(label, category=self.categories[label]),
        }

    def _make_datapipe(
        self,
        resource_dps: List[IterDataPipe],
        *,
        config: DatasetConfig,
        decoder: Optional[Callable[[io.IOBase], torch.Tensor]],
    ) -> IterDataPipe[Dict[str, Any]]:

        images_dp = resource_dps[0]
        images_dp = Filter(images_dp, path_comparator("suffix", ".ppm"))

        if config["split"] == "train":
            dp = Mapper(images_dp, self._append_label_train)
        else:
            ground_truth_dp = resource_dps[1]

            fieldnames = ["Filename", "Width", "Height", "Roi.X1", "Roi.Y1", "Roi.X2", "Roi.Y2", "ClassId"]
            ground_truth_dp = CSVDictParser(ground_truth_dp, fieldnames=fieldnames, delimiter=";", skip_lines=1)

            dp = Zipper(images_dp, ground_truth_dp)
            dp = Mapper(dp, self._append_label_test)

        dp = hint_sharding(dp)
        dp = hint_shuffling(dp)

        dp = Mapper(dp, partial(self._collate, decoder=decoder))
        return dp
