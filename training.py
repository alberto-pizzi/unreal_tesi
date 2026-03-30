# WARNING: edit directory here!
#repo_path = Path(__file__).parent / "unreal_pipeline"
#sys.path.append(str(repo_path))

from typing import Type
import os

import data_enums
from training_models import *
from training_maps import *
from training_dataset_modules import *

# all videos directory
videos_directory = "C:/Users/alber/Downloads/MiniDataset/dataset_copy/rgb_frames"
# destination training directory (where the videos will be copied and organized automatically)
training_base_directory = "C:/Users/alber/Downloads/MiniDataset/training_dataset_accuracy/training_rgb/"
#training_base_directory = "C:/Users/alber/Desktop/ProvaLink/output"
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

    for video_folder in video_folders:
        if video_folder.is_dir():
            emotion_label = adp.get_emotion_label_for_training(video_folder.stem, DatasetClass)

            emotion_label_training_path = train_path / emotion_label.value
            emotion_label_validation_path = train_path / emotion_label.value
            emotion_label_test_path = test_path / emotion_label.value

            emotion_label_training_path.mkdir(parents=True,exist_ok=True)
            emotion_label_validation_path.mkdir(parents=True,exist_ok=True)
            emotion_label_test_path.mkdir(parents=True,exist_ok=True)

            # create symlink to folder
            #TODO add validation dir?
            new_emo_dir = emotion_label_training_path / video_folder.stem
            os.symlink(video_folder, new_emo_dir, target_is_directory=True)

    print("Training directory created")

def create_model_filename(model_name:str, epoch:str) -> str:
    return f'{model_name}_best_model_epoch_{epoch}.pth'

def get_model_type_by_filename(filename:str):
    splits = filename.split("_")

    model_name = splits[0]

    try:
        return ModelType(model_name)
    except ValueError:
        return  None

def build_model(model_type:ModelType, num_classes:int):
    model_class = model_map[model_type]
    model = model_class(num_classes)

    return model


def train_model(
    model,
    criterion,
    optimizer,
    dataloader,
    num_epochs: int,
    print_epoch_window:int = 10
):

    train_losses = []
    best_loss = float('inf')

    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0

        for batch_idx, (batch_videos, batch_labels) in enumerate(dataloader):
            batch_videos = batch_videos.to(device)  # [B, T, C, H, W]
            batch_labels = batch_labels.to(device)

            # it calls forward method
            outputs = model(batch_videos)
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
            new_path = saved_models_dir / create_model_filename(model.model_type.value, str(epoch + 1))
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

            #it calls forward method
            outputs = model(batch_videos)

            pred = outputs.argmax(dim=1)

            correct += (pred == labels).sum().item()
            total += labels.size(0)

    accuracy = correct / total
    return accuracy

def predict_emotion(model, video_folder_path, transform, device, max_frames=16):
    model.eval()

    # load video
    video = load_video_frames(video_folder_path, transform, max_frames)

    # [B=1, T, C, H, W]
    video = video.unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(video) 

    pred = outputs.argmax(dim=1).item()
    confidence = torch.softmax(outputs, dim=1).max().item()

    return pred, confidence

def make_inference(model_checkpoint_path: str, new_video_directory: str, transform):
    model = load_previous_model(model_checkpoint_path)
    model.to(device)

    emotion_id, confidence = predict_emotion(
        model,
        new_video_directory,
        transform,
        device
    )

    emotion_name = adp.d_maps.ID2LABEL.get(emotion_id, "Emotion not found!")

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
    checkpoint_path = Path(model_checkpoint_dir)
    checkpoint_name = checkpoint_path.stem

    model_type = get_model_type_by_filename(checkpoint_name)

    if not model_type:
        raise Exception("No model detected in: ", checkpoint_path)

    model = build_model(model_type,num_classes)
    model.load_state_dict(torch.load(checkpoint_path))
    model.to(device)


    return model

if __name__ == "__main__":

    #create_training_directory(adp.Dataset_CREMA_D)

    root = Path(train_path)
    # data augmentation
    transform = get_transform()

    sampling_type = SamplingType.CONSECUTIVE

    #dataloader = create_dataloader(root, batch_size=8, transform=transform)
    dataloader = DataLoader(FrameDataset(root,transform,sampling_type=sampling_type), batch_size=8, shuffle=True)

    print("Sampling type: ",dataloader.dataset.sampling_type.value)
    print(f"Dataset size: {len(dataloader.dataset)}")
    print(f"Num batches: {len(dataloader)}")


    num_classes = len(data_enums.Emotions)
    print(f"Num emotions: {num_classes}")

    #model = ResNetFrameModel(num_classes)
    model = Conv3DModel(num_classes)
    model.to(device)

    print("Model used: ", model.model_type.value)

    # loss and optimizer definition
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-4)


    num_epochs = 2  # number of epochs

    trained_model, train_losses, best_loss = train_model(
        model=model,
        criterion=criterion,
        optimizer=optimizer,
        dataloader=dataloader,
        num_epochs=num_epochs,
    )

    test_dataloader = DataLoader(FrameDataset(test_path,transform,sampling_type=sampling_type), batch_size=8, shuffle=True)

    test_accuracy = evaluate_model(model=trained_model, dataloader=test_dataloader)
    print(f"Test accuracy: {test_accuracy:.2%}")

    # inference
    new_video_directory = ""
    model_checkpoint_dir = ""
    #make_inference(model_checkpoint_dir,new_video_directory,transform)
