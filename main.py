import os.path

import unreal
import sequencer_manager
import csv_to_face_animation as anim_creator
from csv_to_face_animation import attach_anim_sequence_to_face

METAHUMANS_INSTALLED = [
    "Bryan",

]



if __name__ == "__main__":

    # returns csv file list with extension ".csv" with directory as input
    csv_files = anim_creator.get_csv_file_list(anim_creator.CSV_PATH)






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
















