import unreal
import time

MH_BASE_PATH = "/Game/MetaHumans/"
LS_BASE_PATH = "/Game/LevelSequences/"
LS_PATH_TMP = "/Game/" #TODO to be delete

def create_level_sequence(ls_name):
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    factory = unreal.LevelSequenceFactoryNew()
    ls = asset_tools.create_asset(ls_name, LS_BASE_PATH, unreal.LevelSequence, factory)
    if ls:
        print("Level Sequence Created Successfully!")
    else:
        print("Failed to create Level Sequence!")
    return ls

# TODO to be finish
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

def add_spawnable_actor_into_ls(level_sequence, actor_class):
    if level_sequence and actor_class:
        ls_subsystem = unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem)
        spawnable_binding = ls_subsystem.add_spawnable_from_class(level_sequence,actor_class)
        print("Spawnable Metahuman added:", spawnable_binding)
    else:
        print("Level sequence or actor class not found or nor loaded.")

def load_level_sequence(seq_filename:str):
    full_path = LS_PATH_TMP + seq_filename + "." + seq_filename
    level_sequence = unreal.load_asset(full_path)
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

# FIXME fix location setting
def set_spawnable_actor_location(binding_actor):
    transform_tracks = binding_actor.find_tracks_by_type(unreal.MovieScene3DTransformTrack)
    if transform_tracks:
        transform_track = transform_tracks[0]
        sections = transform_track.get_sections()
        if sections:
            section = sections[0]
            print(section)
            location_x_channel = section.get_channels()[0]  # Channel X
            location_y_channel = section.get_channels()[1]  # Channel Y
            location_z_channel = section.get_channels()[2]  # Channel Z

            new_location = unreal.Vector(270,30,0)

            location_x_channel.add_key(unreal.FrameNumber(0),new_location.x)
            location_y_channel.add_key(unreal.FrameNumber(0),new_location.y)
            location_z_channel.add_key(unreal.FrameNumber(0),new_location.z)


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
    ls = load_level_sequence("NewLevelSequence")
    print(ls)
    mh_class = load_actor_class("Bryan")
    print(mh_class)
    #add_spawnable_actor_into_ls(ls,mh_class)

    #set_spawnable_actor_location(find_spawnable_bindings_by_substring(ls, "BP_Bryan")[0])

    unreal.LevelSequenceEditorBlueprintLibrary.refresh_current_level_sequence()

    #actors = [actor]
    #add_actors_to_sequencer(sequence_filename,actors)


    #camera_actor = spawn_camera_actor(actor)

    #visible(actor,False)




    print("Fine Main!")

