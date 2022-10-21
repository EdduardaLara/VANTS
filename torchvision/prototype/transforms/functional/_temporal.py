import torch

from torchvision.prototype import features


def uniform_temporal_subsample(
    inpt: features.TensorVideoTypeJIT, num_samples: int, temporal_dim: int = -4
) -> features.InputTypeJIT:
    if isinstance(inpt, torch.Tensor) and (torch.jit.is_scripting() or not isinstance(inpt, features.Video)):
        return uniform_temporal_subsample_video(inpt, num_samples, temporal_dim=temporal_dim)
    else:  # isinstance(inpt, features.Video)
        if temporal_dim != -4:
            raise ValueError("Video inputs must have temporal_dim equal to -4")
        output = uniform_temporal_subsample_video(
            inpt.as_subclass(torch.Tensor), num_samples, temporal_dim=temporal_dim
        )
        return features.Video.wrap_like(inpt, output)


def uniform_temporal_subsample_video(video: torch.Tensor, num_samples: int, temporal_dim: int = -4) -> torch.Tensor:
    t_max = video.size(temporal_dim) - 1
    indices = torch.linspace(0, t_max, num_samples, device=video.device).clamp_(0, t_max).long()
    return torch.index_select(video, temporal_dim, indices)
