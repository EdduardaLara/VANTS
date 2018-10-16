import torch
from torch.autograd import gradcheck

from torchvision import layers


import unittest


class ROIPoolTester(unittest.TestCase):

    def test_roi_pool_basic_cpu(self):
        dtype = torch.float32
        device = torch.device('cpu')
        x = torch.rand(1, 1, 10, 10, dtype=dtype, device=device)
        rois = torch.tensor([[0, 0, 0, 4, 4]],  # format is (xyxy)
                            dtype=dtype, device=device)

        pool_h, pool_w = (5, 5)
        roi_pool = layers.ROIPool((pool_h, pool_w), 1)
        y = roi_pool(x, rois)

        gt_y = torch.zeros(rois.size(0), x.size(1), pool_h, pool_w)

        for n in range(0, gt_y.size(0)):
            start_h, end_h = int(rois[n, 2].item()), int(rois[n, 4].item()) + 1
            start_w, end_w = int(rois[n, 1].item()), int(rois[n, 3].item()) + 1
            roi_x = x[:, :, start_h:end_h, start_w:end_w]
            bin_h, bin_w = roi_x.size(2) // pool_h, roi_x.size(3) // pool_w
            for j in range(0, pool_h):
                for i in range(0, pool_w):
                    gt_y[n, :, j, i] = torch.max(roi_x[:, :, j * bin_h:(j + 1) * bin_h, i * bin_w:(i + 1) * bin_w])

        assert torch.equal(gt_y, y), 'ROIPool layer incorrect'

    def test_roi_pool_cpu(self):
        dtype = torch.float32
        device = torch.device('cpu')
        x = torch.rand(2, 1, 10, 10, dtype=dtype, device=device)
        rois = torch.tensor([[0, 0, 0, 9, 9],  # format is (xyxy)
                             [0, 0, 5, 4, 9],
                             [0, 5, 5, 9, 9],
                             [1, 0, 0, 9, 9]],
                            dtype=dtype, device=device)

        pool_h, pool_w = (5, 5)
        roi_pool = layers.ROIPool((pool_h, pool_w), 1)
        y = roi_pool(x, rois)

        gt_y = torch.zeros(rois.size(0), x.size(1), pool_h, pool_w, device=device)
        for n in range(0, gt_y.size(0)):
            for r, roi in enumerate(rois):
                if roi[0] == n:
                    start_h, end_h = int(roi[2].item()), int(roi[4].item()) + 1
                    start_w, end_w = int(roi[1].item()), int(roi[3].item()) + 1
                    roi_x = x[roi[0].long():roi[0].long() + 1, :, start_h:end_h, start_w:end_w]
                    bin_h, bin_w = roi_x.size(2) // pool_h, roi_x.size(3) // pool_w
                    for j in range(0, pool_h):
                        for i in range(0, pool_w):
                            gt_y[r, :, j, i] = torch.max(gt_y[r, :, j, i],
                                                         torch.max(roi_x[:, :,
                                                                         j * bin_h:(j + 1) * bin_h,
                                                                         i * bin_w:(i + 1) * bin_w])
                                                         )

        assert torch.equal(gt_y, y), 'ROIPool layer incorrect'

    def test_roi_pool_gradient_cpu(self):
        dtype = torch.float32
        device = torch.device('cpu')
        layer = layers.ROIPool((5, 5), 1).to(dtype=dtype, device=device)
        x = torch.ones(1, 1, 10, 10, dtype=dtype, device=device, requires_grad=True)
        cx = torch.ones(1, 1, 10, 10, dtype=dtype, requires_grad=True).cuda()
        rois = torch.tensor([
            [0, 0, 0, 9, 9],
            [0, 0, 5, 4, 9],
            [0, 0, 0, 4, 4]],
            dtype=dtype, device=device)

        y = layer(x, rois)
        s = y.sum()
        s.backward()

        gt_grad = torch.tensor([[[[2., 1., 2., 1., 2., 0., 1., 0., 1., 0.],
                                  [1., 1., 1., 1., 1., 0., 0., 0., 0., 0.],
                                  [2., 1., 2., 1., 2., 0., 1., 0., 1., 0.],
                                  [1., 1., 1., 1., 1., 0., 0., 0., 0., 0.],
                                  [2., 1., 2., 1., 2., 0., 1., 0., 1., 0.],
                                  [1., 1., 1., 1., 1., 0., 0., 0., 0., 0.],
                                  [2., 1., 2., 1., 2., 0., 1., 0., 1., 0.],
                                  [1., 1., 1., 1., 1., 0., 0., 0., 0., 0.],
                                  [2., 1., 2., 1., 2., 0., 1., 0., 1., 0.],
                                  [1., 1., 1., 1., 1., 0., 0., 0., 0., 0.]]]], device=device)

        assert torch.equal(x.grad, gt_grad), 'gradient incorrect for roi_pool'

    @unittest.skipIf(not torch.cuda.is_available(), "CUDA unavailable")
    def test_roi_pool_basic_cuda(self):
        dtype = torch.float32
        device = torch.device('cuda')
        x = torch.rand(1, 1, 10, 10, dtype=dtype, device=device)
        rois = torch.tensor([[0, 0, 0, 4, 4]],  # format is (xyxy)
                            dtype=dtype, device=device)

        pool_h, pool_w = (5, 5)
        roi_pool = layers.ROIPool((pool_h, pool_w), 1)
        y = roi_pool(x, rois)

        gt_y = torch.zeros(rois.size(0), x.size(1), pool_h, pool_w)

        for n in range(0, gt_y.size(0)):
            start_h, end_h = int(rois[n, 2].item()), int(rois[n, 4].item()) + 1
            start_w, end_w = int(rois[n, 1].item()), int(rois[n, 3].item()) + 1
            roi_x = x[:, :, start_h:end_h, start_w:end_w]
            bin_h, bin_w = roi_x.size(2) // pool_h, roi_x.size(3) // pool_w
            for j in range(0, pool_h):
                for i in range(0, pool_w):
                    gt_y[n, :, j, i] = torch.max(roi_x[:, :, j * bin_h:(j + 1) * bin_h, i * bin_w:(i + 1) * bin_w])

        assert torch.equal(gt_y.cuda(), y), 'ROIPool layer incorrect'

    @unittest.skipIf(not torch.cuda.is_available(), "CUDA unavailable")
    def test_roi_pool_cuda(self):
        dtype = torch.float32
        device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        x = torch.rand(2, 1, 10, 10, dtype=dtype, device=device)
        rois = torch.tensor([[0, 0, 0, 9, 9],  # format is (xyxy)
                             [0, 0, 5, 4, 9],
                             [0, 5, 5, 9, 9],
                             [1, 0, 0, 9, 9]],
                            dtype=dtype, device=device)

        pool_h, pool_w = (5, 5)
        roi_pool = layers.ROIPool((pool_h, pool_w), 1)
        y = roi_pool(x, rois)

        gt_y = torch.zeros(rois.size(0), x.size(1), pool_h, pool_w, device=device)
        for n in range(0, gt_y.size(0)):
            for r, roi in enumerate(rois):
                if roi[0] == n:
                    start_h, end_h = int(roi[2].item()), int(roi[4].item()) + 1
                    start_w, end_w = int(roi[1].item()), int(roi[3].item()) + 1
                    roi_x = x[roi[0].long():roi[0].long() + 1, :, start_h:end_h, start_w:end_w]
                    bin_h, bin_w = roi_x.size(2) // pool_h, roi_x.size(3) // pool_w
                    for j in range(0, pool_h):
                        for i in range(0, pool_w):
                            gt_y[r, :, j, i] = torch.max(gt_y[r, :, j, i],
                                                         torch.max(roi_x[:, :,
                                                                         j * bin_h:(j + 1) * bin_h,
                                                                         i * bin_w:(i + 1) * bin_w])
                                                         )

        assert torch.equal(gt_y.cuda(), y), 'ROIPool layer incorrect'

    @unittest.skipIf(not torch.cuda.is_available(), "CUDA unavailable")
    def test_roi_pool_gradient_cuda(self):
        dtype = torch.float32
        device = torch.device('cuda')
        layer = layers.ROIPool((5, 5), 1).to(dtype=dtype, device=device)
        x = torch.ones(1, 1, 10, 10, dtype=dtype, device=device, requires_grad=True)
        rois = torch.tensor([
            [0, 0, 0, 9, 9],
            [0, 0, 5, 4, 9],
            [0, 0, 0, 4, 4]],
            dtype=dtype, device=device)

        def func(input):
            return layer(input, rois)

        x.requires_grad = True
        y = layer(x, rois)
        # print(argmax, argmax.shape)
        s = y.sum()
        s.backward()
        gt_grad = torch.tensor([[[[2., 1., 2., 1., 2., 0., 1., 0., 1., 0.],
                                  [1., 1., 1., 1., 1., 0., 0., 0., 0., 0.],
                                  [2., 1., 2., 1., 2., 0., 1., 0., 1., 0.],
                                  [1., 1., 1., 1., 1., 0., 0., 0., 0., 0.],
                                  [2., 1., 2., 1., 2., 0., 1., 0., 1., 0.],
                                  [1., 1., 1., 1., 1., 0., 0., 0., 0., 0.],
                                  [2., 1., 2., 1., 2., 0., 1., 0., 1., 0.],
                                  [1., 1., 1., 1., 1., 0., 0., 0., 0., 0.],
                                  [2., 1., 2., 1., 2., 0., 1., 0., 1., 0.],
                                  [1., 1., 1., 1., 1., 0., 0., 0., 0., 0.]]]], device=device)

        assert torch.equal(x.grad, gt_grad), 'gradient incorrect for roi_pool'


class ROIAlignTester(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        torch.manual_seed(123)
        cls.dtype = torch.float32
        cls.x = torch.rand(1, 1, 10, 10, dtype=cls.dtype)
        cls.single_roi = torch.tensor([[0, 0, 0, 4, 4]],  # format is (xyxy)
                                      dtype=cls.dtype)
        cls.rois = torch.tensor([[0, 0, 0, 9, 9],  # format is (xyxy)
                                 [0, 0, 5, 4, 9],
                                 [0, 5, 5, 9, 9]],
                                dtype=torch.float32)

        cls.gt_y_single = torch.tensor([[[[0.41617328, 0.5040753, 0.25266218, 0.4296828, 0.29928464],
                                          [0.5210769, 0.57222337, 0.2524979, 0.32063985, 0.32635176],
                                          [0.73108256, 0.6114335, 0.62033176, 0.8188273, 0.5562218],
                                          [0.83115816, 0.70803946, 0.7084047, 0.74928707, 0.7769296],
                                          [0.54266506, 0.45964524, 0.5780159, 0.80522037, 0.7321807]]]])

        cls.gt_y_multiple = torch.tensor([[[[0.49311584, 0.35972416, 0.40843594, 0.3638034, 0.49751836],
                                            [0.70881474, 0.75481665, 0.5826779, 0.34767765, 0.46865487],
                                            [0.4740328, 0.69306874, 0.3617804, 0.47145438, 0.66130304],
                                            [0.6861706, 0.17634538, 0.47194335, 0.42473823, 0.37930614],
                                            [0.62666404, 0.49973848, 0.37911576, 0.5842756, 0.7176864]]],
                                          [[[0.67499936, 0.6607055, 0.42656037, 0.46134934, 0.42144877],
                                            [0.7471722, 0.7235433, 0.14512213, 0.13031253, 0.289369],
                                              [0.8443615, 0.6659734, 0.23614208, 0.14719573, 0.4268827],
                                              [0.69429564, 0.5621515, 0.5019923, 0.40678093, 0.34556213],
                                              [0.51315194, 0.7177093, 0.6494485, 0.6775592, 0.43865064]]],
                                          [[[0.24465509, 0.36108392, 0.64635646, 0.4051828, 0.33956185],
                                            [0.49006107, 0.42982674, 0.34184104, 0.15493104, 0.49633422],
                                              [0.54400194, 0.5265246, 0.22381854, 0.3929715, 0.6757667],
                                              [0.32961223, 0.38482672, 0.68877804, 0.71822757, 0.711909],
                                              [0.561259, 0.71047884, 0.84651315, 0.8541089, 0.644432]]]])

    def test_roi_align_basic_cpu(self):
        device = torch.device('cpu')
        self.x = self.x.to(device)
        self.single_roi = self.single_roi.to(device)
        self.gt_y_multiple = self.gt_y_multiple.to(device)

        pool_h, pool_w = (5, 5)
        roi_align = layers.ROIAlign((pool_h, pool_w), spatial_scale=1, sampling_ratio=2.0)
        y = roi_align(self.x, self.single_roi)

        assert torch.equal(self.gt_y_single, y), 'ROIAlign layer incorrect for single ROI on CPU'

    def test_roi_align_cpu(self):
        device = torch.device('cpu')
        self.x = self.x.to(device)
        self.rois = self.rois.to(device)
        self.gt_y_multiple = self.gt_y_multiple.to(device)

        pool_h, pool_w = (5, 5)
        roi_align = layers.ROIAlign((pool_h, pool_w), spatial_scale=1, sampling_ratio=2.0)
        y = roi_align(self.x, self.rois)

        assert torch.equal(self.gt_y_multiple, y), 'ROIAlign layer incorrect for multiple ROIs on CPU'

    @unittest.skipIf(not torch.cuda.is_available(), "CUDA unavailable")
    def test_roi_align_basic_cuda(self):
        device = torch.device('cuda')
        self.x = self.x.to(device)
        self.single_roi = self.single_roi.to(device)
        self.gt_y_single = self.gt_y_single.to(device)

        pool_h, pool_w = (5, 5)
        roi_align = layers.ROIAlign((pool_h, pool_w), spatial_scale=1, sampling_ratio=2.0)
        y = roi_align(self.x, self.single_roi)

        assert torch.allclose(self.gt_y_single, y), 'ROIAlign layer incorrect for single ROI on CUDA'

    @unittest.skipIf(not torch.cuda.is_available(), "CUDA unavailable")
    def test_roi_align_cuda(self):
        device = torch.device('cuda')
        self.x = self.x.to(device)
        self.rois = self.rois.to(device)
        self.gt_y_multiple = self.gt_y_multiple.to(device)

        pool_h, pool_w = (5, 5)
        roi_align = layers.ROIAlign((pool_h, pool_w), spatial_scale=1, sampling_ratio=2.0)
        y = roi_align(self.x, self.rois)

        assert torch.allclose(self.gt_y_multiple, y), 'ROIAlign layer incorrect for multiple ROIs on CUDA'


if __name__ == '__main__':
    unittest.main()
