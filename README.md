
> [!WARNING]
> This repository is still under active development and updating...


>  [!CAUTION]
> Be carefull. Not all files are "ready-to-use" at now...
> 
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
> [!WARNING]
> Some files or directories may be refactored...
>

-`main.py`: It is the main file, 

- `a2f_2_csv_batch.py`: get CSV files in batch from NVIDIA Audio2Face API. Some parameters can be set at the beginning of the file.
- `a2f_involved_rig_maps.py`: it contains only dictionaries for mapping *ARKit blendshapes* into **Control Rig Involved**.
- `audio_dataset_maps.py`: it contains only enumarations and dictionaries to quickly process audio datasets.
- `audio_dataset_processing.py`: it contains classes with rules and logics for elaborate every type of dataset. In this way we can combine different dataset, just add the relative class here for elaborate it.
- `control_rig_processing.py`: this file is used for process different control rig maps making sure they match.
- `control_rig_classes.py`: this file contains **control rig overrides**. That is, all those control rigs that aren't of the default type (float) but of more complex types. Therefore, they require aggregating and calculating the blendshapes because it's not possible to simply map them one-to-one.
- `csv_to_face_animation.py`: this file is used for create an animation (keyframes and bake) starting from CSV.
- `sequencer_manager.py`: it takes care of managing every actions can we do into Sequencer, like spawn/despawn MetaHumans, import animations, import audio, ecc..
- ...


> [!IMPORTANT]
> If you want to override a control rig, you have to **CREATE** its *own class* into `control_rig_classes.py`, managing the calculation/mapping logic. Then, you have to **ADD** *rig name* followed by the *class* (previusly created) into dictionary.
>


## How pipeline works

This pipeline is thinked to executend into 3 step (or 2: step 1 and 2 can be merged).

1. Launch `a2f_2_csv_batch.py` (from wherever you want) for call NVIDIA Audio2Face API to get CSV files in batch. But before, you have to download only **A2F Python Client**, you can do it following the guide put in the requirements. 
2. Launch  `main.py` from Unreal Engine (Editor or [CLI](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python)). It will use other file **not** mentioned in this paragraph.
3. Render entire queues saved by Unreal Editor or by Python scirpt (to be fixed, but not relevent for rendering video)
4. ...

## Requirements

- Unreal Engine 5.6 with Python API and Movie Render Queue Plugin, better with Windows 10/11 with complete compatibility.
- Python 3.9 (with standard libraries (csv,os,pathlib)
- Unreal library for Python (settable as *python stub*)
- [A2F Python Client](https://build.nvidia.com/nvidia/audio2face-3d/api)
- [NVIDIA Audio2Face API](https://build.nvidia.com/nvidia/audio2face-3d) access.
- [Frames2Ev](https://github.com/MagriniGabriele/Frames2Ev) by *Gabriele Magrini*, to generate event-frames from video
- [rpg_vid2e](https://github.com/uzh-rpg/rpg_vid2e), for Frames2Ev.
- ...
