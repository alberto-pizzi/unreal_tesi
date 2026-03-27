from pathlib import Path
import sys

# WARNING: edit directory here!
#repo_path = Path(__file__).parent / "unreal_pipeline"
#sys.path.append(str(repo_path))
import audio_dataset_processing as adp


from PIL import Image
from enum import Enum
from typing import Type
import shutil
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import numpy as np
import torch.nn as nn
import torchvision.models as models
import torch.optim as optim

import data_enums

# all videos directory
videos_directory = "C:/Users/alber/Downloads/MiniDataset/dataset_copy/rgb_frames"
# destination training directory (where the videos will be copied and organized automatically)
training_base_directory = "C:/Users/alber/Downloads/MiniDataset/training_dataset_accuracy/training_rgb/"
#training_base_directory = "C:/Users/alber/Downloads/MiniDataset/training_dataset/training_rgb"

videos_path = Path(videos_directory)
training_path = Path(training_base_directory)
train_path = training_path / "train"
val_path = training_path / "val"
test_path = training_path / "test"
saved_models_dir = Path('./saved_models')
saved_models_dir.mkdir(exist_ok=True)


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)



def get_video_folders(directory:Path):
    # list of all folder into directory
    folders = [p for p in directory.iterdir() if p.is_dir()]

    return folders

def create_training_directory(DatasetClass:Type[adp.AudioDatasetParser]):

    video_folders = get_video_folders(videos_path)

    train_path.mkdir(exist_ok=True)
    val_path.mkdir(exist_ok=True)

    for video_folder in video_folders:
        emotion_label = adp.get_emotion_label_for_training(video_folder.stem, DatasetClass)

        emotion_label_training_path = train_path / emotion_label.value
        emotion_label_validation_path = train_path / emotion_label.value
        emotion_label_test_path = test_path / emotion_label.value

        emotion_label_training_path.mkdir(exist_ok=True)
        emotion_label_validation_path.mkdir(exist_ok=True)
        emotion_label_test_path.mkdir(exist_ok=True)

        #TODO add validation dir?
        shutil.copytree(video_folder, emotion_label_training_path / video_folder.stem, dirs_exist_ok=True)

    print("Training directory created")

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



def create_dataloader(root_dir, batch_size=2, shuffle=True, transform=None):
    dataset = FrameDataset(root_dir, transform)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)



def build_resnet_model(num_classes):
    resnet = models.resnet18(pretrained=True)
    #nn.stm
    resnet.fc = nn.Linear(resnet.fc.in_features, num_classes)  # edit last layer
    resnet = resnet.to(device)
    return resnet

def frame_voting(model,batch_videos):
    frame_preds = []
    for t in range(batch_videos.shape[1]):  # iterate over frames
        frame_pred = model(batch_videos[:, t])  # ResNet per frame
        frame_preds.append(frame_pred)
    return frame_preds

def train_model(
    model,
    criterion,
    optimizer,
    dataloader,
    num_epochs: int = 10,
    print_epoch_window:int = 10
):

    train_losses = []
    best_loss = float('inf')

    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0

        for batch_idx, (batch_videos, batch_labels) in enumerate(dataloader):
            batch_videos = batch_videos.to(device)
            batch_labels = batch_labels.to(device)

            # frame-level predictions
            frame_preds = frame_voting(model, batch_videos)

            outputs = torch.stack(frame_preds).mean(dim=0)  # frame voting
            loss = criterion(outputs, batch_labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

            if batch_idx % 1 == 0:
                print(f'Epoch {epoch + 1}, Batch {batch_idx}, Loss: {loss.item():.4f}')

        avg_loss = running_loss / len(dataloader)
        train_losses.append(avg_loss)

        # save best model
        if avg_loss < best_loss:
            best_loss = avg_loss
            new_path = saved_models_dir / f'best_emotion_model_epoch{epoch + 1}.pth'
            torch.save(model.state_dict(), new_path)
            print(f"BEST MODEL SAVED! Epoch {epoch + 1}, Loss: {avg_loss:.4f}")
        else:
            print(f"Epoch {epoch + 1}/{num_epochs}, AVG Loss: {avg_loss:.4f}")

    print("TRAINING COMPLETED!")
    print(f"Best loss: {best_loss:.4f}")
    return model, train_losses, best_loss

def evaluate_model(model, dataloader):

    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for batch_videos, labels in dataloader:
            batch_videos = batch_videos.to(device)
            labels = labels.to(device)

            frame_preds = frame_voting(model, batch_videos)
            outputs = torch.stack(frame_preds).mean(dim=0)

            pred = outputs.argmax(dim=1)

            correct += (pred == labels).sum().item()
            total += labels.size(0)

    accuracy = correct / total
    return accuracy

def predict_emotion(model, video_folder_path, transform, max_frames=16):

    dataset = FrameDataset(str(video_folder_path), transform=transform, max_frames=max_frames)
    dataloader = DataLoader(dataset, batch_size=1, shuffle=False)

    model.eval()  # inference mod
    predictions = []

    with torch.no_grad():  # no gradient
        for batch_videos, _ in dataloader:  # ignore label (new video)
            batch_videos = batch_videos.to(device)

            # same training frame voting
            frame_preds = frame_voting(model, batch_videos)

            video_pred = torch.stack(frame_preds).mean(dim=0)
            predictions.append(video_pred)

    final_pred = torch.stack(predictions).mean(dim=0)
    emotion_idx = final_pred.argmax().item()
    confidence = torch.softmax(final_pred, dim=0).max().item()

    return emotion_idx, confidence

def make_inference(model_checkpoint_dir:str,new_video_directory:str, transform):
    num_classes = len(data_enums.Emotions)
    model = build_resnet_model(num_classes)
    model.load_state_dict(torch.load(Path(model_checkpoint_dir)))
    model.to(device)

    new_video_path = Path(new_video_directory)
    # prediction
    emotion_id, confidence = predict_emotion(model, new_video_path, transform, device)

    emotion_name = adp.d_maps.ID2LABEL[emotion_id]

    if not emotion_name:
        emotion_name = "Emotion not found!"

    print(f"Emotion: {emotion_name}")
    print(f"Confidence: {confidence:.2%}")

def get_transform():
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    return transform

def load_previous_model(model_checkpoint_dir:str):
    num_classes = len(data_enums.Emotions)
    model = build_resnet_model(num_classes)
    model.load_state_dict(torch.load(Path(model_checkpoint_dir)))
    model.to(device)

    return model

def train_from_checkpoint(model_checkpoint_dir:str,new_data_path,num_epochs:int):
    model = load_previous_model(model_checkpoint_dir)

    transform = get_transform()
    new_dataloader = create_dataloader(new_data_path, batch_size=8)

    optimizer = optim.Adam(model.parameters(), lr=1e-5)
    criterion = nn.CrossEntropyLoss()

    return train_model(model=model,criterion=criterion,optimizer=optimizer,dataloader=new_dataloader,num_epochs=num_epochs,transform=transform)


if __name__ == "__main__":

    #create_training_directory(adp.Dataset_CREMA_D)

    root = Path(train_path)
    # data augmentation
    transform = get_transform()

    dataloader = create_dataloader(root, batch_size=8, transform=transform)

    print(f"Dataset size: {len(dataloader.dataset)}")
    print(f"Num batches: {len(dataloader)}")


    num_classes = len(data_enums.Emotions)
    print(f"Num emotions: {num_classes}")

    model = build_resnet_model(num_classes)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-4)


    num_epochs = 10  # number of epochs

    trained_model, train_losses, best_loss = train_model(
        model=model,
        criterion=criterion,
        optimizer=optimizer,
        dataloader=dataloader,
        num_epochs=num_epochs,
    )

    test_dataloader = create_dataloader(test_path, batch_size=8, transform=transform)
    test_accuracy = evaluate_model(model=trained_model, dataloader=test_dataloader)
    print(f"Test accuracy: {test_accuracy:.2%}")

    # inference
    new_video_directory = ""
    model_checkpoint_dir = ""
    #make_inference(model_checkpoint_dir,new_video_directory,transform, device)
