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
from torchvision.models.video import mvit_v2_s, r3d_18, R3D_18_Weights

# WARNING: use ONLY strings written as a single word, without spaces or special characters
class ModelType(Enum):
    RESNET = "resnet"
    RESNET_LSTM = "resnetlstm"
    CONV3D = "conv3d"
    VIDEO_TRANSFORMER = "videotransformer"


class ResNetFrameModel(nn.Module):
    model_type = ModelType.RESNET

    def __init__(self,num_classes:int):
        super().__init__()
        self.resnet = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        self.resnet.fc = nn.Linear(self.resnet.fc.in_features, num_classes)
        # device not needed


    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, T, C, H, W]
        # B = batch size ; T = number of frame per video
        B, T, C, H, W = x.shape
        x = x.reshape(B*T, C, H, W)
        out = self.resnet(x)
        out = out.reshape(B, T, -1) # with -1 PyTorch calculate remaining dimension automatically
        out = out.mean(dim=1) #average on frames

        return out

class ResNetLSTMModel(nn.Module):
    model_type = ModelType.RESNET_LSTM

    def __init__(self, num_classes, lstm_hidden_size=256, lstm_layers=1):
        super().__init__()
        self.resnet = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        self.resnet.fc = nn.Identity()  # take feature vector [B*T, 512]
        self.lstm = nn.LSTM(input_size=512, hidden_size=lstm_hidden_size, num_layers=lstm_layers, batch_first=True)
        self.fc = nn.Linear(lstm_hidden_size, num_classes)

    def forward(self, x):
        # x: [B, T, C, H, W]
        B, T, C, H, W = x.shape
        x = x.reshape(B*T, C, H, W)
        features = self.resnet(x)        # [B*T, 512]
        features = features.reshape(B, T, -1)  # [B, T, 512]
        lstm_out, _ = self.lstm(features)   # [B, T, hidden_size]
        #out = lstm_out[:, -1, :]            # uses last time-step
        out = lstm_out.mean(dim=1)
        out = self.fc(out)                   # [B, num_classes]
        return out

class Conv3DModel(nn.Module):
    model_type = ModelType.CONV3D

    def __init__(self, num_classes):
        super().__init__()
        self.model = r3d_18(weights=R3D_18_Weights.DEFAULT)
        self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)

    def forward(self, x):
        # x: [B, T, C, H, W]
        x = x.permute(0, 2, 1, 3, 4).contiguous()  # -> [B, C, T, H, W]
        return self.model(x)


class VideoTransformerModel(nn.Module):
    model_type = ModelType.VIDEO_TRANSFORMER

    def __init__(self, num_classes):
        super().__init__()

        self.model = mvit_v2_s(weights="DEFAULT")  # pretrained

        # replace last classifier
        if isinstance(self.model.head, nn.Sequential):
            in_features = self.model.head[-1].in_features  # last layer
            self.model.head[-1] = nn.Linear(in_features, num_classes)
        else:
            in_features = self.model.head.in_features
            self.model.head = nn.Linear(in_features, num_classes)

    def forward(self, x):
        # x: [B, C, T, H, W]
        x = x.permute(0, 2, 1, 3, 4).contiguous()  # -> [B, C, T, H, W]
        return self.model(x)