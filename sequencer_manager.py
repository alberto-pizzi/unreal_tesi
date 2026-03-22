import unreal
import time
from pathlib import Path

# WARNING: insert keyframes and bake animation first (for playback times)
# IMPORTANT :Unreal accepts ONLY paths UNIX-like


#TODO edit paths

AUDIO_ASSETS_PATH = "/Game/AudioAssetImported/"

ANIMATION_PATH = "/Game/MetaHumans/Animations/CustomAnimations/"

MH_BASE_PATH = "/Game/MetaHumans/"
LS_BASE_PATH = "/Game/LevelSequences/"
LS_PATH_TMP = "/Game/" #TODO to be delete

camera_settings = {
    "AspectRatio": 1.2,
    "FieldOfView": 85.0,
}

def create_level_sequence(ls_name):
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    factory = unreal.LevelSequenceFactoryNew()
    ls = asset_tools.create_asset(ls_name, LS_BASE_PATH, unreal.LevelSequence, factory)
    if ls:
        print("Level Sequence Created Successfully!")
    else:
        print("Failed to create Level Sequence!")
    return ls

# TODO to be finish (maybe it will not be used)
'''
def mrq_export_ls_to_video(ls_filename):
    # Carica il MoviePipelineQueueSubsystem per accedere alla coda render
    mrq_subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
    if not mrq_subsystem:
        unreal.log_error("Movie Render Queue subsystem non disponibile")
        return

    # Crea un nuovo job per la tua Level Sequence (assumendo tu conosca il percorso asset)
    queue = mrq_subsystem.get_queue()
    job = queue.allocate_new_job(unreal.MoviePipelineExecutorJob)

    level_sequence_path = "/Game/PROFILO.PROFILO"
    sequence = unreal.load_asset(level_sequence_path)
    #job.set_sequence(sequence)
    #job.sequence = sequence
    job.set_editor_property("sequence",sequence)
    job.set_editor_property("map", unreal.EditorLevelLibrary.get_editor_world().get_name())

    # Imposta output directory
    output_setting = job.get_configuration().find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
    output_setting.output_directory = unreal.DirectoryPath("/Game/Saved/MovieRenders/NativeMP4")

    # Aggiungi la configurazione video MP4 nativa (usa H.264)
    video_setting = job.get_configuration().find_or_add_setting_by_class(unreal.MoviePipelineVideoOutputSetting)

    video_setting.file_name_format = "{sequence_name}_export"


    video_setting.codec = unreal.MoviePipelineVideoCodec.H264
    # Imposta formato di output nativo MP4 con codec H.264
    video_setting.video_codec = unreal.SimpleVideoCodec.H264
    video_setting.output_file_extension = "mp4"
'''

def add_spawnable_actor_into_ls(level_sequence, actor_class):
    spawnable_binding = None
    if level_sequence and actor_class:
        ls_subsystem = unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem)
        spawnable_binding = ls_subsystem.add_spawnable_from_class(level_sequence,actor_class)
        print("Spawnable Metahuman added:", spawnable_binding)
    else:
        print("Level sequence or actor class not found or nor loaded.")

    return spawnable_binding

def get_ls_path(seq_filename:str):
    full_path = LS_PATH_TMP + seq_filename + "." + seq_filename
    return full_path


def load_level_sequence(seq_filename:str):
    level_sequence = unreal.load_asset(get_ls_path(seq_filename))
    return level_sequence

def get_mh_base_path(mh_name:str):
    base_path = MH_BASE_PATH + mh_name + "/"
    return base_path

def get_mh_class_path(mh_name:str):
    path = get_mh_base_path(mh_name) + "BP_" + mh_name + ".BP_" + mh_name
    return path

def load_actor_class(mh_name:str):
    bp_path = get_mh_class_path(mh_name)
    bp_class = unreal.EditorAssetLibrary.load_blueprint_class(bp_path)
    return bp_class

def find_spawnable_bindings_by_substring(level_sequence, substring):
    substring = substring.lower()
    matches = []

    for binding in level_sequence.get_spawnables():
        if substring in str(binding.get_display_name()).lower():
            matches.append(binding)

    return matches

# FIXME check for end_frame location actor spawning
def set_location_rotation_of_element(element_binding, location:list, rotation:list, start_frame:int, end_frame:int):
    transformations = element_binding.find_tracks_by_type(unreal.MovieScene3DTransformTrack)

    if transformations:
        transform_track = transformations[0]
    else:
        transform_track = element_binding.add_track(unreal.MovieScene3DTransformTrack)

    sections = transform_track.get_sections()
    if sections:
        section = sections[0]
    else:
        section = transform_track.add_section()

    section.set_range(start_frame, end_frame)

    channels = section.get_all_channels()

    start_frame_fn  = unreal.FrameNumber(start_frame)
    end_frame_fn  = unreal.FrameNumber(end_frame)

    # locations (x,y,x)
    channels[0].add_key(start_frame_fn, location[0])
    channels[1].add_key(start_frame_fn, location[1])
    channels[2].add_key(start_frame_fn, location[2])

    channels[0].add_key(end_frame_fn, location[0])
    channels[1].add_key(end_frame_fn, location[1])
    channels[2].add_key(end_frame_fn, location[2])

    # rotations
    channels[3].add_key(start_frame_fn, rotation[0])
    channels[4].add_key(start_frame_fn, rotation[1])
    channels[5].add_key(start_frame_fn, rotation[2])

    channels[3].add_key(end_frame_fn, rotation[0])
    channels[4].add_key(end_frame_fn, rotation[1])
    channels[5].add_key(end_frame_fn, rotation[2])

    print("Location and rotation have been set!")

# TODO add aspect ratio and fov settings?
def add_camera_into_sequencer(level_sequence, location:list, rotation:list):
    if len(location) != 3 or len(rotation) != 3:
        raise TypeError("Expected 3 values for location and rotation lists")

    ls_system = unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem)

    spawnable_camera_binding = ls_system.add_spawnable_from_class(level_sequence,unreal.CameraActor)

    start_frame = level_sequence.get_playback_start()
    end_frame = level_sequence.get_playback_end()

    set_location_rotation_of_element(spawnable_camera_binding, location, rotation, start_frame, end_frame)

    return spawnable_camera_binding

def set_property_camera(level_sequence, camera_settings:dict,start_frame:int, end_frame:int):

    binding = level_sequence.find_binding_by_name("CameraComponent")

    tracks = binding.find_tracks_by_type(unreal.MovieSceneFloatTrack)

    for setting_name,setting_value in camera_settings.items():
        track = get_or_create_float_track(binding,tracks, setting_name, setting_name)
        sections = track.get_sections()
        if sections:
            section = sections[0]
        else:
            section = track.add_section()

        float_channels = section.get_all_channels()

        section.set_range(start_frame, end_frame)

        start_frame_fn = unreal.FrameNumber(start_frame)
        end_frame_fn = unreal.FrameNumber(end_frame)

        float_channels[0].add_key(start_frame_fn, setting_value)
        float_channels[0].add_key(end_frame_fn, setting_value)




# TODO to be delete
    '''for track in tracks:
        print(track.get_display_name())

        sections = track.get_sections()
        if sections:
            section = sections[0]
            print(section)
            float_channels = section.get_all_channels()
            print("canali float: ", len(float_channels))
            print("canale: ", float_channels)
            float_channels[0].add_key(unreal.FrameNumber(0),100)

            for channel in float_channels:
                value = "Field Of View"
                if channel.get_name() == value:
                    print("Trovato con nome ",value)
                    break
                value = "FieldOfView"
                if channel.get_name() == value:
                    print("Trovato con nome ",value)
                    break'''


def get_or_create_float_track(camera_component_binding, tracks, property_name, property_path):
    float_track = None
    for track in tracks:
        if str(track.get_property_name()) == property_name:
            print("trovato: ", property_name)
            return track

    if not float_track:
        float_track = camera_component_binding.add_track(unreal.MovieSceneFloatTrack)
        float_track.set_property_name_and_path(property_name, property_path)
        print("creato: ", property_name)

    return float_track


def add_cut_camera_into_sequencer(level_sequence, camera_binding):
    camera_cut_track = level_sequence.add_track(unreal.MovieSceneCameraCutTrack)

    sections = camera_cut_track.get_sections()
    for section in sections:
        camera_cut_track.remove_section(section)

    camera_cut_section = camera_cut_track.add_section()
    camera_cut_section.set_range(level_sequence.get_playback_start(), level_sequence.get_playback_end())

    camera_cut_section.set_camera_binding_id(level_sequence.get_binding_id(camera_binding))

    print("Camera Cut Track has been set!")


def select_actor(mh_official_name):
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    all_elements = actor_subsystem.get_all_level_actors()
    real_actor = None
    for actor in all_elements:
        if mh_official_name in actor.get_name():
            real_actor = actor
            break
    return real_actor

def spawn_metahuman(mh_official_name):
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    bp_path = get_mh_class_path(mh_official_name)
    # insert here coordinates
    location = unreal.Vector(0,0,0)
    rotation = unreal.Rotator(0, 0, 0)
    bp_class = unreal.EditorAssetLibrary.load_blueprint_class(bp_path)
    new_actor = actor_subsystem.spawn_actor_from_class(bp_class, location, rotation)
    print("Spawned!")
    return new_actor

def despawn_metahuman(actor_obj):
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    return actor_subsystem.destroy_actor(actor_obj)

def despawn_metahumans(actor_objs):
    for actor_obj in actor_objs:
        despawn_metahuman(actor_obj)

def spawn_camera_actor(actor_obj):
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    camera_class = unreal.CameraActor.static_class()

    skeletal = actor_obj.get_component_by_class(unreal.SkeletalMeshComponent)
    head_transform = skeletal.get_socket_transform("head", unreal.RelativeTransformSpace.RTS_WORLD)
    head_location = head_transform.translation
    offset = unreal.Vector(0, 40, 4)
    camera_location = head_location + offset
    rotation = unreal.Rotator(0.0, 0.0, -90.0)

    # Spawn del CameraActor nella posizione e rotazione specificate
    actor_camera = actor_subsystem.spawn_actor_from_class(camera_class, camera_location, rotation)

    #imposta parametri di fuoco
    camera_component = actor_camera.get_component_by_class(unreal.CameraComponent.static_class())
    camera_component.set_editor_property("field_of_view",75.0)
    camera_component.set_editor_property("aspect_ratio", 1.5)

    if actor_camera:
        actor_camera.set_actor_label("ActorCam")
    else:
        unreal.log_warning("Spawn Actor fallito")

    return actor_camera

def despawn_camera_actor(actor_camera_obj):
    despawn_metahuman(actor_camera_obj)

def visible(actor_obj,is_visible):
    actor_obj.set_is_temporarily_hidden_in_editor(not is_visible)

def get_audio_asset_path(asset_filename:str):
    full_path = AUDIO_ASSETS_PATH + asset_filename + "." + asset_filename
    return full_path

def add_audio_track_into_sequencer(level_sequence,audio_asset):
    audio_track = level_sequence.add_track(unreal.MovieSceneAudioTrack)
    start_frame = level_sequence.get_playback_start()
    end_frame = level_sequence.get_playback_end()
    audio_section = audio_track.add_section()
    audio_section.set_sound(audio_asset)

    audio_section.set_range(start_frame, end_frame)

    #unreal.EditorAssetLibrary.save_asset(level_sequence.get_path_name())


def get_audio_asset(asset_filename: str):
    audio_asset = unreal.EditorAssetLibrary.load_asset(get_audio_asset_path(asset_filename))
    if not audio_asset:
        unreal.log_warning(f"Asset not found: {asset_filename}")
        return None
    return audio_asset


def import_audio_as_assets(audio_filename_paths: list[Path]):
    for filename in audio_filename_paths:
        import_audio_as_asset(filename)

def import_audio_as_asset(audio_filename_path: Path):
    # IMPORTANT :Unreal accepts ONLY paths unix-like
    wav_file_path = audio_filename_path.as_posix()

    task = unreal.AssetImportTask()
    task.filename = wav_file_path
    task.destination_path = AUDIO_ASSETS_PATH
    task.automated = True
    task.save = True
    task.replace_existing = True

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

    if task.imported_object_paths:
        unreal.log("Audio import done! Asset created: {}".format(task.imported_object_paths[0]))
    else:
        unreal.log_warning("Audio import failed!")


def remove_face_control_rig_track(level_sequence):
    binding = level_sequence.find_binding_by_name("Face")

    tracks = binding.find_tracks_by_type(unreal.MovieSceneControlRigParameterTrack)

    for track in tracks:
        binding.remove_track(track)


def add_possessable_actor_into_ls(actor_obj):
    ls_system = unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem)
    bindings = ls_system.add_actors([actor_obj])

    print("Added possessable actor into sequencer!")


# Only for possessable actors as input
def calculate_camera_pos(actor_obj):
    skeletal = actor_obj.get_component_by_class(unreal.SkeletalMeshComponent)
    head_transform = skeletal.get_socket_transform("head", unreal.RelativeTransformSpace.RTS_WORLD)
    head_location = head_transform.translation
    offset = unreal.Vector(0, 40, 4)
    camera_location = head_location + offset
    rotation = unreal.Rotator(0.0, 0.0, -90.0)

    location_list = [camera_location.x,camera_location.y,camera_location.z]
    rotation_list = [rotation.roll, rotation.pitch, rotation.yaw]

    return location_list, rotation_list

def load_anim_sequence(anim_seq_filename:str):
    full_path = ANIMATION_PATH + anim_seq_filename + "." + anim_seq_filename
    anim_sequence = unreal.load_asset(full_path)
    return anim_sequence

# TODO could be improved giving animation sequence instead filename?
#WARNING: Metahumans into level sequence must be only ONE!
def attach_anim_sequence_to_face(level_sequence,anim_seq_filename:str):
    binding = level_sequence.find_binding_by_name("Face")

    anim_sequence = load_anim_sequence(anim_seq_filename)

    animation_length_seconds = anim_sequence.get_play_length()

    frame_rate = level_sequence.get_display_rate()
    fps = frame_rate.numerator / frame_rate.denominator

    animation_length_frames = int(animation_length_seconds * fps)

    # FIXME is correct pos?
    '''
    level_sequence.set_playback_start(0)
    level_sequence.set_playback_end(animation_length_frames)'''

    anim_track = binding.add_track(unreal.MovieSceneSkeletalAnimationTrack)
    anim_section = anim_track.add_section()
    anim_section.set_range(0, animation_length_frames)
    anim_section.params.animation = anim_sequence

    unreal.LevelSequenceEditorBlueprintLibrary.refresh_current_level_sequence()
    unreal.EditorAssetLibrary.save_asset(level_sequence.get_path_name())

    print("Attached animation sequence to face done successfully!")

def clear_sequencer(level_sequence):

    bindings = level_sequence.get_bindings()
    tracks = level_sequence.get_tracks()

    for binding in bindings:
        binding.remove()

    for track in tracks:
        level_sequence.remove_track(track)



if __name__ == "__main__":
    print("Inizio Main!")
    ''' 
   actor = select_actor("Bernice")
    if actor:
        print("Attore selezionato")
        despawn_metahuman(actor)
        print("Despawn termianto")
    else:
        print("Non selezionato")
    
    sequence_filename = "PrimaSequenza"
    actor = spawn_metahuman("Bernice")
    ls = create_level_sequence(sequence_filename)
    '''
    #ls = load_level_sequence("SeqVM")
    ls = load_level_sequence("SeqVM")
    print(ls)

    #mh_class = load_actor_class("Bryan")
    #print(mh_class)

    #ottieni_pos_rig(ls)
    '''  
    actor_obj = spawn_metahuman("Bryan")
    add_possessable_actor_into_ls(actor_obj)

    clear_sequencer(ls)

    despawn_metahumans([actor_obj])

      
    actor_obj = spawn_metahuman("Bryan")
    add_possessable_actor_into_ls(actor_obj)
    location, rotation = calculate_camera_pos(actor_obj)
    camera_binding = add_camera_into_sequencer(ls,location,rotation)
    add_cut_camera_into_sequencer(ls,camera_binding)

    attach_anim_sequence_to_face(ls,"NewFluidAnimation")

    add_audio_track_into_sequencer(ls, get_audio_asset("out"))

    remove_face_control_rig_track(ls)
    '''







    #stampa_tutto(ls)
    #remove_face_control_rig_track(ls)
    #set_spawnable_actor_location(find_spawnable_bindings_by_substring(ls, "BP_Bryan")[0])

    #camera_binding = add_camera_into_sequencer(ls,[241, 90, 148],[0, 0, -90])
    #set_property_camera(ls, camera_settings,0,380)
    #add_cut_camera_into_sequencer(ls,camera_binding)


    #add_audio_track_into_sequencer(ls,get_audio_asset("1001_DFA_HAP_XX"))

    unreal.LevelSequenceEditorBlueprintLibrary.refresh_current_level_sequence()

    #actors = [actor]
    #add_actors_to_sequencer(sequence_filename,actors)


    #camera_actor = spawn_camera_actor(actor)

    #visible(actor,False)




    print("Fine Main!")

