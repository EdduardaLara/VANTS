#include <ATen/ATen.h>
#include <ATen/native/quantized/affine_quantizer.h>
#include <torch/library.h>

namespace vision {
namespace ops {

namespace {

template <typename scalar_t>
at::Tensor qnms_kernel_impl(
    const at::Tensor& dets,
    const at::Tensor& scores,
    double iou_threshold) {

  TORCH_CHECK(!dets.is_cuda(), "dets must be a CPU tensor");
  TORCH_CHECK(!scores.is_cuda(), "scores must be a CPU tensor");
  TORCH_CHECK(
      dets.scalar_type() == scores.scalar_type(),
      "dets should have the same type as scores");

  if (dets.numel() == 0)
    return at::_empty_affine_quantized({0}, dets.options()); 

  const auto ndets = dets.size(0);
  const double dets_scale = dets.q_scale();


  auto x1_t = dets.select(1, 0).contiguous();
  auto y1_t = dets.select(1, 1).contiguous();
  auto x2_t = dets.select(1, 2).contiguous();
  auto y2_t = dets.select(1, 3).contiguous();
  auto order_t = std::get<1>(scores.sort(0, /* descending=*/true));
  at::Tensor suppressed_t = at::zeros({ndets}, dets.options().dtype(at::kByte));
  at::Tensor keep_t = at::zeros({ndets}, dets.options().dtype(at::kLong));
  at::Tensor areas_t = at::zeros({ndets}, dets.options().dtype(at::kFloat));

  auto suppressed = suppressed_t.data_ptr<uint8_t>();
  auto keep = keep_t.data_ptr<int64_t>();
  auto order = order_t.data_ptr<int64_t>();
  auto x1 = x1_t.data_ptr<scalar_t>();
  auto y1 = y1_t.data_ptr<scalar_t>();
  auto x2 = x2_t.data_ptr<scalar_t>();
  auto y2 = y2_t.data_ptr<scalar_t>();
  auto areas = areas_t.data_ptr<float>();

  auto areas_a = areas_t.accessor<float, 1>();
  for (int64_t i = 0; i < ndets; i++) {
    areas_a[i] = dets_scale * dets_scale * (x2[i].val_ - x1[i].val_) * (y2[i].val_ - y1[i].val_);
  }

  int64_t num_to_keep = 0;

  for (int64_t _i = 0; _i < ndets; _i++) {
    auto i = order[_i];
    if (suppressed[i] == 1)
      continue;
    keep[num_to_keep++] = i;

    auto ix1val = x1[i].val_;
    auto iy1val = y1[i].val_;
    auto ix2val = x2[i].val_;
    auto iy2val = y2[i].val_;
    auto iarea = areas[i];

    for (int64_t _j = _i + 1; _j < ndets; _j++) {
      auto j = order[_j];
      if (suppressed[j] == 1)
        continue;
      auto xx1 = std::max(ix1val, x1[j].val_);
      auto yy1 = std::max(iy1val, y1[j].val_);
      auto xx2 = std::min(ix2val, x2[j].val_);
      auto yy2 = std::min(iy2val, y2[j].val_);

      float w = dets_scale * std::max(0, xx2 - xx1);
      float h = dets_scale * std::max(0, yy2 - yy1);
      auto inter = w * h;
      auto ovr = inter / (iarea + areas[j] - inter);
      if (ovr > iou_threshold)
        suppressed[j] = 1;
    }
  }
  return keep_t.narrow(/*dim=*/0, /*start=*/0, /*length=*/num_to_keep);
}

at::Tensor qnms_kernel(
    const at::Tensor& dets,
    const at::Tensor& scores,
    double iou_threshold) {
  TORCH_CHECK(
      dets.dim() == 2, "boxes should be a 2d tensor, got ", dets.dim(), "D");
  TORCH_CHECK(
      dets.size(1) == 4,
      "boxes should have 4 elements in dimension 1, got ",
      dets.size(1));
  TORCH_CHECK(
      scores.dim() == 1,
      "scores should be a 1d tensor, got ",
      scores.dim(),
      "D");
  TORCH_CHECK(
      dets.size(0) == scores.size(0),
      "boxes and scores should have same number of elements in ",
    "dimension 0, got ",
    dets.size(0),
    " and ",
    scores.size(0));

  auto result = at::empty({0});

  AT_DISPATCH_QINT_TYPES(dets.scalar_type(), "qnms_kernel", [&] {
    result = qnms_kernel_impl<scalar_t>(dets, scores, iou_threshold);
  });
  return result;
}

} // namespace

TORCH_LIBRARY_IMPL(torchvision, QuantizedCPU, m) {
  m.impl(TORCH_SELECTIVE_NAME("torchvision::nms"), TORCH_FN(qnms_kernel));
}

} // namespace ops
} // namespace vision
