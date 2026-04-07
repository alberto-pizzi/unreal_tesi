

# Development of a processing pipeline to simulate neuromorphic event streams and train neural networks for emotion recognition via animated humanoids.

## Some Audio Dataset

- [CREMA-D](https://github.com/CheyneyComputerScience/CREMA-D)
- [RAVDESS](https://zenodo.org/records/1188976)

## Pipeline structure

1. Take an **audio dataset** (for example .wav) with each track **labeled**.
2. Batch call **NVIDIA Audio2Face API** from Python script to get its corrisponding CSV file. It will contain all **ARKit blendshapes** for each frame generated from an input audio at 30 FPS.
3. Map every ARKit blendshapes into *MetaHuman Facial Control Rigs*.
4. Set keyframes starting from with values read from CSV file.
5. Bake into *Animation Sequence* all animation composed by keyframes have been set.
6. Create full single MetaHuman animation, setting tracks into *Sequencer* like audio, camera, and *Animation Sequece* (obtained from bake, in the previous step).
7. Import and Render each *Level Sequences* into *Movie Render Queue*. The goal is obtain **.mp4** video with audio with specific resolution (for example 1280x720). 
8. Generate *event-frames* of mp4 rendered video, using **Frames2Ev**, in batch on mp4 video rendered.
9. Train a neural network to recognize emotions with event-frames as input.

> [!NOTE]
> One *Level Sequence* contains **ONLY ONE** scene with one MetaHuman.



## How this directory works


-`main.py`: It is the main file, 

- `a2f_2_csv_batch.py`: get CSV files in batch from NVIDIA Audio2Face API. Some parameters can be set at the beginning of the file.
- `a2f_involved_rig_maps.py`: it contains only dictionaries for mapping *ARKit blendshapes* into **Control Rig Involved**.
- `audio_dataset_maps.py`: it contains only enumarations and dictionaries to quickly process audio datasets.
- `audio_dataset_processing.py`: it contains classes with rules and logics for elaborate every type of dataset. In this way we can combine different dataset, just add the relative class here for elaborate it.
- `control_rig_processing.py`: this file is used for process different control rig maps making sure they match.
- `control_rig_classes.py`: this file contains **control rig overrides**. That is, all those control rigs that aren't of the default type (float) but of more complex types. Therefore, they require aggregating and calculating the blendshapes because it's not possible to simply map them one-to-one.
- `control_rig_maps.py`: it contains only dictionaries with control rig overrides.
- `csv_to_face_animation.py`: this file is used for create an animation (keyframes and bake) starting from CSV.
- `sequencer_manager.py`: it takes care of managing every actions can we do into Sequencer, like spawn/despawn MetaHumans, import animations, import audio, ecc..
- ...


> [!IMPORTANT]
> If you want to override a control rig, you have to **CREATE** its *own class* into `control_rig_classes.py`, managing the calculation/mapping logic. Then, you have to **ADD** *rig name* followed by the *class* (previusly created) into `control_rig_maps.py` dictionary.
>


## How pipeline works

This pipeline is thinked to executend into 3 step (or 2: step 1 and 2 can be merged).

1. Run `a2f_2_csv_batch.py` (from wherever you want) for call NVIDIA Audio2Face API to get CSV files in batch. But before, you have to download only **A2F Python Client**, you can do it following the guide put in the requirements. 
2. Run  `main.py` from Unreal Engine (Editor or [CLI](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python)). It will use other file **not** mentioned in this paragraph.
3. Render entire queues saved by Unreal Editor or by Python scirpt (to be fixed, but not relevent for rendering video)
4. ...

### How to config Unreal Engine to run main.py

Actually, `main.py` execute pipeline **from** generating animation sequences **to** importing all levels sequences created into Movie Render Queue (MRQ).


1. Download and Run Unreal Engine 5.6+ (better for Windows 10/11)
2. Create new **GAME** project, as **C++** project. Blank project is ok.
3. Make sure you have installed (or intall) following plugins from `Edit -> Plugin`: **Python Editor Script Plugin**,**Sequencer Scripting**, **Movie Render Queue** and **MetaHuman SDK**. Then restart editor, if needed.
4. Create (or open) a level from `File -> New Level` or `File -> Open Level`
5. Intall (download and **add**) MetaHumans into you project: from `Window -> QuxelBridge`, you can follow [this videoguide](https://youtu.be/3H7pHTArkaU). **IMPORTANT:** To check if they have been correctly added to the project, you should see a new folder (into game path in *Content Browser*) called "MetaHumans" with inside some subfolder called like your MetaHumans added...
6. Go to game path `/Game/Content/` and create new folder called `Python`. In this folder you have to put *every* python script (like this repo). If you prefer, link files will be fine too.
7. Go into `config.py` and set parameters. specially you have to add yours **MetaHumans official names** (it is case sensitive) into `METAHUMANS_INSTALLED` list. Then you should set paths (making the distinction between game path and absolute paths). Game paths **always start** from `/Game/` folder. **IMPORTANT:** Make sure that *every* game path folder into `config.py` really exists. **Boolean variables at the beginning are essential** because you should able/disable some part of pipeline.
8. Create a **render settings asset file** and **render queue asset file** into path set into `config.py`. To make this, you should go to MRQ from `Window -> Cinematics -> Movie Render Queue` and then **set and export** these assets into **their respective game paths**. Then you have to *update* `config.py` with their names, if you haven't already done so.

<!-- You can run [CLI](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python) -->

> [!NOTE]
> If Unreal Editor crash often, set `IMPORT_AUDIO_ASSETS = False` into `config.py` and then **import manually** audio assets into game path written inside `config.py`. If crashes continues, 


### How rendering works

> [!IMPORTANT]
> Before reder, you make sure **render setting asset file** and **render queue asset file** already exist.
>

If you have all *Level Sequences*, you are able to render with MRQ. Let's distinguish between the origin of the level sequences:

- ***Level Sequences* generated with `main.py`**: if you set `IMPORT_ALL_LS_INTO_MRQ = True` into `config.py`, the **render queue asset file** previously created, will be populated.


## How to setup to training

Function allowed are only: **train**, **evaluate** and **inference**. So you should set main with operations needed.

1. Install conda env importing `training_environment.yml`
2. Open `training.py`
3. Set paths at the beginning of the file
4. If needed, set trasformations into `get_strasform()` or create new trasformations
5. Go into main (in the same file)
6. Turn on or call `create_training_directory`, at the beggining of main, for creating labeled directories for training and testing.
7. Set `sampling_type`
8. Set DataLoader call with own paramters as: `dataset`, `batch_size` and `shuffle`
9. Set `model`, choosing right model class
10. Set loss type (`criterion`) and `optimizer`
11. Set `num_epochs`
12. Call the right function based on the type of operation: `train_model(...)`, `evaluate_model(...)` or `make_inference(...)`. Also read following banner.
14. Turn off or remove useless code lines

> [!IMPORTANT]
> If you pass `val_dataloader` at `train_model(...)` function, it will also make evaluation for each apoch during training (useful for stats). Otherwise **leave blank**.
> 
## Requirements

- Unreal Engine 5.6 with Python API and Movie Render Queue Plugin, better with Windows 10/11 with complete compatibility.
- Python 3.9 (with standard libraries (csv,os,pathlib))
- Unreal library for Python (settable as *python stub*)
- [A2F Python Client](https://build.nvidia.com/nvidia/audio2face-3d/api)
- [NVIDIA Audio2Face API](https://build.nvidia.com/nvidia/audio2face-3d) access.
- [Frames2Ev](https://github.com/MagriniGabriele/Frames2Ev) by *Gabriele Magrini*, to generate event-frames from video
- [rpg_vid2e](https://github.com/uzh-rpg/rpg_vid2e), for Frames2Ev.
- ...
