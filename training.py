# WARNING: edit directory here!
#repo_path = Path(__file__).parent / "unreal_pipeline"
#sys.path.append(str(repo_path))

from typing import Type
import os

import data_enums
from training_models import *
from training_maps import *
from training_dataset_modules import *
import matplotlib.pyplot as plt
from pathlib import Path
import time

# all videos directory
#videos_directory = "C:/Users/alber/Downloads/MiniDataset/dataset_copy/rgb_frames"
videos_directory = "C:/Users/alber/Desktop/TrainingDef/rgb_frames"
# destination training directory (where the videos will be copied and organized automatically)
training_base_directory = "C:/Users/alber/Desktop/TrainingDef/training_dir"
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

# WARNING: if you pass also val_dataloader as parameter, train_model will also make evaluation each epoch
def train_model(model, criterion, optimizer, num_epochs: int, train_dataloader, val_dataloader=None,
                print_epoch_window: int = 10):

    train_losses = []
    train_accuracies = []
    val_losses = []
    val_accuracies = []
    best_loss = float('inf')

    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for batch_idx, (batch_videos, batch_labels) in enumerate(train_dataloader):
            batch_videos = batch_videos.to(device)  # [B, T, C, H, W]
            batch_labels = batch_labels.to(device)

            # it calls forward method
            outputs = model(batch_videos)
            loss = criterion(outputs, batch_labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            preds = outputs.argmax(dim=1)
            correct += (preds == batch_labels).sum().item()
            total += batch_labels.size(0)


        avg_train_loss = running_loss / len(train_dataloader)
        train_acc = correct / total
        train_losses.append(avg_train_loss)
        train_accuracies.append(train_acc)

        # optional evaluation
        if val_dataloader is not None:
            val_loss, val_acc = evaluate_model(model, val_dataloader)
            val_losses.append(val_loss)
            val_accuracies.append(val_acc)
        else:
            val_loss, val_acc = None, None

        print(f"Epoch {epoch+1}/{num_epochs} | "
              f"Train Loss: {avg_train_loss:.4f}, Train Acc: {train_acc:.4f} | "
              f"Val Loss: {val_loss if val_loss is not None else 'N/A'} | "
              f"Val Acc: {val_acc if val_acc is not None else 'N/A'}")

        # save best model
        if avg_train_loss < best_loss:
            best_loss = avg_train_loss
            torch.save(model.state_dict(),
                       saved_models_dir / create_model_filename(model.model_type.value, str(epoch + 1)))
            print(f"BEST MODEL SAVED! Epoch {epoch+1}")

    print("TRAINING COMPLETED!")
    print(f"Best loss: {best_loss:.4f}")
    return model, train_losses, train_accuracies, val_losses, val_accuracies

def evaluate_model(model, dataloader):

    model.eval()
    correct = 0
    total = 0
    running_loss = 0.0

    with torch.no_grad():
        for batch_videos, labels in dataloader:
            batch_videos = batch_videos.to(device)
            labels = labels.to(device)

            #it calls forward method
            outputs = model(batch_videos)

            loss = criterion(outputs, labels)
            running_loss += loss.item() * labels.size(0)

            pred = outputs.argmax(dim=1)

            correct += (pred == labels).sum().item()
            total += labels.size(0)

    avg_loss = running_loss / total
    accuracy = correct / total
    return avg_loss,accuracy


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

def draw_loss_graph(y_loss_train, y_loss_val,model_name:str, save_path="plot/loss_plot.png"):
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    epochs = range(1, len(y_loss_train) + 1)
    plt.figure(figsize=(10, 4))
    plt.plot(epochs, y_loss_train, 'o-', label='Training Loss')
    if y_loss_val is not None:
        plt.plot(epochs, y_loss_val, 's-', label='Validation Loss')
    plt.title('Loss by Epoch for ' + model_name + " model")
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

def draw_acc_graph(y_acc_train, y_acc_val,model_name:str, save_path="plot/accuracy_plot.png"):
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    epochs = range(1, len(y_acc_train) + 1)
    plt.figure(figsize=(10, 4))
    plt.plot(epochs, y_acc_train, 'o-', label='Training Accuracy')
    if y_acc_val is not None:
        plt.plot(epochs, y_acc_val, 's-', label='Validation Accuracy')
    plt.title('Accuracy by Epoch for ' + model_name + " model")
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


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
    model = ResNetLSTMModel(num_classes)
    model.to(device)

    print("Model used: ", model.model_type.value)

    # loss and optimizer definition
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-4)


    num_epochs = 50  # number of epochs


    test_dataloader = DataLoader(FrameDataset(test_path,transform,sampling_type=sampling_type), batch_size=8, shuffle=True)

    start = time.time()
    # training (and evaluation)
    trained_model, train_losses, train_accuracies, val_losses, val_accuracies = train_model(
        model=model,
        criterion=criterion,
        optimizer=optimizer,
        train_dataloader=dataloader,
        val_dataloader=test_dataloader,
        num_epochs=num_epochs,
    )
    end = time.time()
    time_seconds = end - start
    time_minutes = time_seconds / 60
    print(f"Time elapsed: {time_minutes:.2f} seconds")
    print(f"Training time: {time_minutes:.4f} minutes")
    draw_loss_graph(train_losses, val_losses,model.model_type.value)
    draw_acc_graph(train_accuracies, val_accuracies,model.model_type.value)


    model_checkpoint_dir = "C:/Users/alber/PycharmProjects/PythonProject1/saved_models/conv3d_best_model_epoch_20.pth"
    #test_accuracy = evaluate_model(model=load_previous_model(model_checkpoint_dir), dataloader=test_dataloader)
    #print(f"Test accuracy: {test_accuracy:.2%}")

    # inference

    new_video_directory = "C:/Users/alber/Desktop/TrainingDef/training_dir/test/happy/Kellan_1027_WSI_HAP_XX"

    #make_inference(model_checkpoint_dir,new_video_directory,transform)
