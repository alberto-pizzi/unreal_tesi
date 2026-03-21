import os.path

import unreal
import sequencer_manager
import csv_to_face_animation as anim_creator
from pathlib import Path


# TODO to be completed
METAHUMANS_INSTALLED = [
    "Bryan",

]

# it scans directories and subdirectories, return a list of Path
def collect_filenames_path_by_extension(directory: str, extension: str) -> list[Path]:
    extension = extension.lower()
    path = Path(directory)

    if not path.is_dir():
        raise ValueError(f"Directory not valid: {directory}")

    file_list = [p for p in path.rglob(f"*{extension}") if p.is_file()]
    return file_list


if __name__ == "__main__":

    # returns csv file list with extension ".csv" with directory as input
    csv_files = anim_creator.get_csv_file_list(anim_creator.CSV_PATH) #TODO replace with collect_filenames_path_by_extension?

    #import audio as assets
    #audio_file_paths = collect_filenames_path_by_extension()


    for mh_name in METAHUMANS_INSTALLED:
        mh_class = sequencer_manager.load_actor_class(mh_name)

        for csv_file in csv_files:
            rows, arkit_csv_names = anim_creator.read_csv(csv_file)

            ls = sequencer_manager.create_level_sequence(mh_name)  # to be fixed

            anim_creator.insert_keyframes(ls, rows)
            animation_sequence_filename = mh_name+"_"+os.path.splitext(csv_file)[0]+"_baked"
            anim_creator.bake_to_animation_sequence(ls,animation_sequence_filename) # FIXME choose filename
            mh_binding = sequencer_manager.add_spawnable_actor_into_ls(ls, mh_class)
            #sequencer_manager.set_location_rotation_of_element(mh_binding,[0,0,0],[0,0,0],)

            anim_creator.attach_anim_sequence_to_face(ls,animation_sequence_filename)
            sequencer_manager.remove_face_control_rig_track(ls)

            # TODO to be finish




            #save
            unreal.EditorAssetLibrary.save_loaded_asset(ls)
















