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

class ModelType(Enum):
    RESNET = "resnet"
    RESNET_LSTM = "resnet_lstm"
    CONV3D = "conv3d"
    VIDEO_TRANSFORMER = "video_transformer"


def uniform_sampling(num_frames,max_frames):
    if num_frames >= max_frames:
        indices = np.linspace(0, num_frames - 1, max_frames, dtype=int)
    else:
        indices = list(range(num_frames)) + [num_frames - 1] * (max_frames - num_frames)

    return indices

# frame dataset with different lengths handling
class FrameDataset(Dataset):
    def __init__(self, root_dir, transform=None, max_frames=16):
        self.root_dir = Path(root_dir)
        self.transform = transform if transform else transforms.ToTensor()
        self.max_frames = max_frames

        self.frame_dirs = []
        self.labels = []

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

        # uniform sampling
        indices = uniform_sampling(num_frames, self.max_frames)

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

class ResNetFrameModel(nn.Module):
    def __init__(self,num_classes:int):
        super().__init__()
        self.resnet = models.resnet18(pretrained=True)
        self.resnet.fc = nn.Linear(self.resnet.fc.in_features, num_classes)
        # device not needed


    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # B = batch size ; T = number of frame per video
        B, T, C, H, W = x.shape
        x = x.view(B*T, C, H, W)
        out = self.resnet(x)
        out = out.view(B, T, -1) # with -1 PyTorch calculate remaining dimension automatically
        out = out.mean(dim=1) #average on frames

        return out
