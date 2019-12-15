from __future__ import division
import torch
import torchvision.transforms as transforms
import torchvision.transforms.functional_tensor as F_t
import torchvision.transforms.functional as F
import numpy as np
import unittest
import random


class Tester(unittest.TestCase):

    def test_vflip(self):
        img_tensor = torch.randn(3, 16, 16)
        img_tensor_clone = img_tensor.clone()
        vflipped_img = F_t.vflip(img_tensor)
        vflipped_img_again = F_t.vflip(vflipped_img)
        self.assertEqual(vflipped_img.shape, img_tensor.shape)
        self.assertTrue(torch.equal(img_tensor, vflipped_img_again))
        self.assertTrue(torch.equal(img_tensor, img_tensor_clone))

    def test_hflip(self):
        img_tensor = torch.randn(3, 16, 16)
        img_tensor_clone = img_tensor.clone()
        hflipped_img = F_t.hflip(img_tensor)
        hflipped_img_again = F_t.hflip(hflipped_img)
        self.assertEqual(hflipped_img.shape, img_tensor.shape)
        self.assertTrue(torch.equal(img_tensor, hflipped_img_again))
        self.assertTrue(torch.equal(img_tensor, img_tensor_clone))

    def test_crop(self):
        img_tensor = torch.randint(0, 255, (3, 16, 16), dtype=torch.uint8)
        img_tensor_clone = img_tensor.clone()
        top = random.randint(0, 15)
        left = random.randint(0, 15)
        height = random.randint(1, 16 - top)
        width = random.randint(1, 16 - left)
        img_cropped = F_t.crop(img_tensor, top, left, height, width)
        img_PIL = transforms.ToPILImage()(img_tensor)
        img_PIL_cropped = F.crop(img_PIL, top, left, height, width)
        img_cropped_GT = transforms.ToTensor()(img_PIL_cropped)
        self.assertTrue(torch.equal(img_tensor, img_tensor_clone))
        self.assertTrue(torch.equal(img_cropped, (img_cropped_GT * 255).to(torch.uint8)),
                        "functional_tensor crop not working")

    def test_adjustments(self):
        fns = ((F.adjust_brightness, F_t.adjust_brightness),
               (F.adjust_contrast, F_t.adjust_contrast),
               (F.adjust_saturation, F_t.adjust_saturation))

        for _ in range(20):
            channels = 3
            dims = torch.randint(1, 50, (2,))
            shape = (channels, dims[0], dims[1])

            if torch.randint(0, 2, (1,)) == 0:
                img = torch.rand(*shape, dtype=torch.float)
            else:
                img = torch.randint(0, 256, shape, dtype=torch.uint8)

            factor = 3 * torch.rand(1)
            img_clone = img.clone()
            for f, ft in fns:

                ft_img = ft(img, factor)
                if not img.dtype.is_floating_point:
                    ft_img = ft_img.to(torch.float) / 255

                img_pil = transforms.ToPILImage()(img)
                f_img_pil = f(img_pil, factor)
                f_img = transforms.ToTensor()(f_img_pil)

                # F uses uint8 and F_t uses float, so there is a small
                # difference in values caused by (at most 5) truncations.
                max_diff = (ft_img - f_img).abs().max()
                self.assertLess(max_diff, 5 / 255 + 1e-5)
                self.assertTrue(torch.equal(img, img_clone))

    def test_rgb_to_grayscale(self):
        img_tensor = torch.randint(0, 255, (3, 16, 16), dtype=torch.uint8)
        img_tensor_clone = img_tensor.clone()
        grayscale_tensor = F_t.rgb_to_grayscale(img_tensor).to(int)
        grayscale_pil_img = torch.tensor(np.array(F.to_grayscale(F.to_pil_image(img_tensor)))).to(int)
        max_diff = (grayscale_tensor - grayscale_pil_img).abs().max()
        self.assertLess(max_diff, 1.0001)
        self.assertTrue(torch.equal(img_tensor, img_tensor_clone))

    def test_center_crop(self):
        img_tensor = torch.randint(0, 255, (1, 32, 32), dtype=torch.uint8)
        img_tensor_clone = img_tensor.clone()
        cropped_tensor = F_t.center_crop(img_tensor, [10, 10])
        cropped_pil_image = F.center_crop(transforms.ToPILImage()(img_tensor), [10, 10])
        cropped_pil_tensor = (transforms.ToTensor()(cropped_pil_image) * 255).to(torch.uint8)
        self.assertTrue(torch.equal(cropped_tensor, cropped_pil_tensor))
        self.assertTrue(torch.equal(img_tensor, img_tensor_clone))

    def test_five_crop(self):
        img_tensor = torch.randint(0, 255, (1, 32, 32), dtype=torch.uint8)
        img_tensor_clone = img_tensor.clone()
        cropped_tensor = F_t.five_crop(img_tensor, [10, 10])
        cropped_pil_image = F.five_crop(transforms.ToPILImage()(img_tensor), [10, 10])
        self.assertTrue(torch.equal(cropped_tensor[0],
                                    (transforms.ToTensor()(cropped_pil_image[0]) * 255).to(torch.uint8)))
        self.assertTrue(torch.equal(cropped_tensor[1],
                                    (transforms.ToTensor()(cropped_pil_image[2]) * 255).to(torch.uint8)))
        self.assertTrue(torch.equal(cropped_tensor[2],
                                    (transforms.ToTensor()(cropped_pil_image[1]) * 255).to(torch.uint8)))
        self.assertTrue(torch.equal(cropped_tensor[3],
                                    (transforms.ToTensor()(cropped_pil_image[3]) * 255).to(torch.uint8)))
        self.assertTrue(torch.equal(cropped_tensor[4],
                                    (transforms.ToTensor()(cropped_pil_image[4]) * 255).to(torch.uint8)))
        self.assertTrue(torch.equal(img_tensor, img_tensor_clone))

    def test_ten_crop(self):
        img_tensor = torch.randint(0, 255, (1, 32, 32), dtype=torch.uint8)
        img_tensor_clone = img_tensor.clone()
        cropped_tensor = F_t.ten_crop(img_tensor, [10, 10])
        cropped_pil_image = F.ten_crop(transforms.ToPILImage()(img_tensor), [10, 10])
        self.assertTrue(torch.equal(cropped_tensor[0],
                                    (transforms.ToTensor()(cropped_pil_image[0]) * 255).to(torch.uint8)))
        self.assertTrue(torch.equal(cropped_tensor[1],
                                    (transforms.ToTensor()(cropped_pil_image[2]) * 255).to(torch.uint8)))
        self.assertTrue(torch.equal(cropped_tensor[2],
                                    (transforms.ToTensor()(cropped_pil_image[1]) * 255).to(torch.uint8)))
        self.assertTrue(torch.equal(cropped_tensor[3],
                                    (transforms.ToTensor()(cropped_pil_image[3]) * 255).to(torch.uint8)))
        self.assertTrue(torch.equal(cropped_tensor[4],
                                    (transforms.ToTensor()(cropped_pil_image[4]) * 255).to(torch.uint8)))
        self.assertTrue(torch.equal(cropped_tensor[5],
                                    (transforms.ToTensor()(cropped_pil_image[5]) * 255).to(torch.uint8)))
        self.assertTrue(torch.equal(cropped_tensor[6],
                                    (transforms.ToTensor()(cropped_pil_image[7]) * 255).to(torch.uint8)))
        self.assertTrue(torch.equal(cropped_tensor[7],
                                    (transforms.ToTensor()(cropped_pil_image[6]) * 255).to(torch.uint8)))
        self.assertTrue(torch.equal(cropped_tensor[8],
                                    (transforms.ToTensor()(cropped_pil_image[8]) * 255).to(torch.uint8)))
        self.assertTrue(torch.equal(cropped_tensor[9],
                                    (transforms.ToTensor()(cropped_pil_image[9]) * 255).to(torch.uint8)))
        self.assertTrue(torch.equal(img_tensor, img_tensor_clone))

    def test_resize(self):
        height = random.randint(24, 32) * 2
        width = random.randint(24, 32) * 2
        img = torch.ones(3, height, width)
        img_clone = img.clone()
        modes = ["bilinear", "nearest", "bicubic"]

        for mode in modes:
            # (Int) for resizing
            output_size = random.randint(5, 12) * 2
            result = F_t.resize(img, output_size, interpolation=mode)
            if height < width:
                self.assertEqual(output_size, result.shape[1])
            else:
                self.assertEqual(output_size, result.shape[2])

            # (Int, Int) for resizing
            output_size = (random.randint(5, 12) * 2, random.randint(5, 12) * 2)
            result = F_t.resize(img, output_size, interpolation=mode)
            self.assertEqual((output_size[0], output_size[1]), (result.shape[1], result.shape[2]))

        # checking input tensor is not mutated
        self.assertTrue(torch.equal(img, img_clone))

        # checking overshooting for bicubic
        output_size = (random.randint(5, 12) * 2, random.randint(5, 12) * 2)
        result = F_t.resize(img, output_size, interpolation="bicubic")
        clamped_tensor = result.clamp(min=0, max=255)
        self.assertTrue(torch.equal(result, clamped_tensor))


if __name__ == '__main__':
    unittest.main()
