from enum import Enum
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import data_enums
from pathlib import Path
import torch.nn as nn
import torchvision.models as models
import torch.optim as optim
import torch
from PIL import Image
import numpy as np
import audio_dataset_processing as adp


def uniform_sampling(num_frames,max_frames):
    if num_frames >= max_frames:
        indices = np.linspace(0, num_frames - 1, max_frames, dtype=int)
    else:
        indices = list(range(num_frames)) + [num_frames - 1] * (max_frames - num_frames)

    return indices

def consecutive_sampling(num_frames, max_frames):
    if num_frames >= max_frames:
        start = np.random.randint(0, num_frames - max_frames + 1)
        return list(range(start, start + max_frames))
    else:
        return list(range(num_frames)) + [num_frames - 1] * (max_frames - num_frames)

def random_sampling(num_frames, max_frames):
    if num_frames >= max_frames:
        # takes max_frames frame random with no repetitions
        indices = np.random.choice(num_frames, size=max_frames, replace=False)
        return sorted(indices)  # orders to hold temporal order
    else:
        # if video is shorter, pad with last frame
        return list(range(num_frames)) + [num_frames - 1] * (max_frames - num_frames)

class SamplingType(Enum):
    UNIFORM = "uniform"
    RANDOM = "random"
    CONSECUTIVE = "consecutive"


sampling_map = {
    SamplingType.UNIFORM: uniform_sampling,
    SamplingType.RANDOM: random_sampling,
    SamplingType.CONSECUTIVE: consecutive_sampling
}

# frame dataset with different lengths handling
class FrameDataset(Dataset):
    def __init__(self, root_dir, transform=None, max_frames=16,sampling_type=SamplingType.UNIFORM):
        self.root_dir = Path(root_dir)
        self.transform = transform if transform else transforms.ToTensor()
        self.max_frames = max_frames


        self.sampling_fn = sampling_map[sampling_type]
        self.sampling_type = sampling_type

        self.frame_dirs = []
        self.labels = []

        # labeling
        for label_name in data_enums.Emotions:
            emotion_label = label_name.value
            emotion_id = adp.d_maps.LABEL2ID[label_name.value]

            label_dir = self.root_dir / emotion_label
            if not label_dir.exists():
                continue
            for video_folder in sorted(label_dir.iterdir()):
                if video_folder.is_dir():
                    self.frame_dirs.append(video_folder)
                    self.labels.append(emotion_id)

    def __len__(self):
        return len(self.frame_dirs)

    def __getitem__(self, idx):
        frame_folder = self.frame_dirs[idx]
        frame_paths = sorted(frame_folder.glob("*.png"))
        num_frames = len(frame_paths)


        indices = self.sampling_fn(num_frames, self.max_frames)

        frames = []
        for i in indices:
            img = Image.open(frame_paths[i]).convert("RGB")
            img = self.transform(img)  # [C, H, W]
            frames.append(img)

        # stack: [T, C, H, W]
        video_tensor = torch.stack(frames)

        # no need to permute, we want [T, C, H, W] for batch -> [batch, T, C, H, W]
        label = self.labels[idx]
        return video_tensor, label


def load_video_frames(videoframes_folder_path, transform=None, max_frames=16, sampling_fn=uniform_sampling):
    frame_paths = sorted(Path(videoframes_folder_path).glob("*.png"))
    num_frames = len(frame_paths)

    if num_frames == 0:
        raise ValueError("No frame found")

    # 🔹 consecutive sampling (consigliato per tutti i tuoi modelli)
    indices = sampling_fn(num_frames, max_frames)

    frames = []
    for i in indices:
        img = Image.open(frame_paths[i]).convert("RGB")
        if transform:
            img = transform(img)
        else:
            img = torch.tensor(np.array(img)).permute(2, 0, 1) / 255.0 # tensor = [C, H, W]
        frames.append(img)

    # [T, C, H, W]
    return torch.stack(frames)