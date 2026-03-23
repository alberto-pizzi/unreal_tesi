import sys
import os

current_dir = os.path.dirname(__file__)
sys.path.append(current_dir)


import unreal
import sequencer_manager
import rendering
import csv_to_face_animation as anim_creator
from pathlib import Path
from config import *


# it scans directories and subdirectories, return a list of Path
def collect_filename_paths_by_extension(directory: str, extension: str) -> list[Path]:
    extension = extension.lower()
    path = Path(directory)

    if not path.is_dir():
        raise ValueError(f"Directory not valid: {directory}")

    file_list = [p for p in path.rglob(f"*{extension}") if p.is_file()]
    return file_list

def get_animation_sequence_filename(primal_audio_filename: str, suffix: str = ""):
    animation_sequence_filename = os.path.splitext(primal_audio_filename)[0] + suffix
    return animation_sequence_filename

def generate_animation(level_sequence,csv_path):
    #primal_audio_filenames = []
    primal_audio_filename = csv_path.parent.name
    #primal_audio_filenames.append(primal_audio_filename)
    rows = anim_creator.read_csv_with_conversion(csv_path)

    anim_creator.insert_keyframes_by_row(level_sequence, rows)
    animation_sequence_filename = get_animation_sequence_filename(primal_audio_filename)
    anim_creator.bake_to_animation_sequence(level_sequence, animation_sequence_filename)  # FIXME choose filename

    return primal_audio_filename

def delete_asset_into_directory(directory:str,asset_name:str):
    unreal.EditorAssetLibrary.delete_asset(directory+asset_name)

def delete_all_assets_into_directory(directory:str):
    asset_paths = unreal.EditorAssetLibrary.list_assets(directory,False,False)

    for asset_path in asset_paths:
        unreal.EditorAssetLibrary.delete_asset(asset_path)

def check_or_create_asset_directory(directory:str):
    if not unreal.EditorAssetLibrary.does_directory_exist(directory):
        unreal.EditorAssetLibrary.make_directory(directory)

def get_asset_names_in_directory(directory_path, recursive=False):
    asset_paths = unreal.EditorAssetLibrary.list_assets(directory_path, recursive=recursive, include_folder=False)
    asset_names = [path.split('/')[-1].split('.')[-1] for path in asset_paths]
    return asset_names

def get_ls_name(mh_name:str,animation_name:str):
    return mh_name + "_" + animation_name

if __name__ == "__main__":

    # TODO connect a2f_2_csv_batch to this py file?

    csv_paths = anim_creator.get_csv_paths_into_subfolders(CSV_FOLDER_PATH)

    if not csv_paths:
        raise ValueError(f"No CSV files found in {CSV_FOLDER_PATH}")

    # WARNING: insert keyframes and bake animation first (for playback times)
    if GENERATE_ANIMATION_SEQUENCE and METAHUMANS_INSTALLED:
        check_or_create_asset_directory(TMP_LS_BASE_PATH)
        delete_all_assets_into_directory(TMP_LS_BASE_PATH)
        check_or_create_asset_directory(ANIMATION_PATH)
        delete_all_assets_into_directory(ANIMATION_PATH)
        ls = sequencer_manager.create_level_sequence("BakingSequence", TMP_LS_BASE_PATH)
        unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(ls)
        mh_class = sequencer_manager.load_actor_class(METAHUMANS_INSTALLED[0])
        for csv_path in csv_paths:
            sequencer_manager.clear_sequencer(ls)
            mh_binding = sequencer_manager.add_spawnable_actor_into_ls(ls, mh_class)
            animation_frame = generate_animation(ls, csv_path)

        sequencer_manager.clear_sequencer(ls)





    animation_sequence_asset_names = get_asset_names_in_directory(ANIMATION_PATH)

    #import audio as assets
    if IMPORT_AUDIO_ASSETS:
        audio_file_paths = collect_filename_paths_by_extension(INPUT_AUDIO_PATH, ".wav")
        sequencer_manager.import_audio_as_assets(audio_file_paths)

    audio_asset_names = get_asset_names_in_directory(AUDIO_ASSETS_PATH)

    camera_locations_and_rotation_by_mh = sequencer_manager.get_actor_cams_locations_and_rotations(METAHUMANS_INSTALLED)

    if GENERATE_LS_FOREACH_MH:

        c = 0
        for mh_name in METAHUMANS_INSTALLED:
            mh_class = sequencer_manager.load_actor_class(mh_name)

            for animation_name in animation_sequence_asset_names:
                c = c + 1

                ls_name = get_ls_name(mh_name,animation_name)
                ls = sequencer_manager.create_level_sequence(ls_name)
                unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(ls)
                mh_binding = sequencer_manager.add_spawnable_actor_into_ls(ls, mh_class)
                #sequencer_manager.set_location_rotation_of_element(mh_binding,[0,0,0],[0,0,0],)
                sequencer_manager.attach_anim_sequence_to_face(ls, animation_name)
                camera_binding = sequencer_manager.add_camera_into_sequencer(ls, camera_locations_and_rotation_by_mh[mh_name][0],
                                                                             camera_locations_and_rotation_by_mh[mh_name][1])
                sequencer_manager.set_property_camera(ls, camera_settings, ls.get_playback_start(), ls.get_playback_end())
                sequencer_manager.add_cut_camera_into_sequencer(ls, camera_binding)



                if MAKE_LS_WITH_AUDIO:
                    audio_asset = sequencer_manager.get_audio_asset(animation_name)
                    sequencer_manager.add_audio_track_into_sequencer(ls,audio_asset)

                sequencer_manager.remove_face_control_rig_track(ls)

                #save
                unreal.EditorAssetLibrary.save_loaded_asset(ls)

        print("Generated ", c, " sequences!")


    if IMPORT_ALL_LS_INTO_MRQ:
        ls_names = get_asset_names_in_directory(LS_BASE_PATH)
        print(ls_names)

        for ls_name in ls_names:
            rendering.import_ls_into_mrq(ls_name,QUEUE_NAME)














