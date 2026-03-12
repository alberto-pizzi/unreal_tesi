import unreal
import time

MH_BASE_PATH = "/Game/MetaHumans/"

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
    bp_path = MH_BASE_PATH + mh_official_name + "/BP_" + mh_official_name + ".BP_" + mh_official_name
    # inserire qui le coordinate se necessario
    location = unreal.Vector(0,0,0)
    rotation = unreal.Rotator(0, 0, 0)
    bp_class = unreal.EditorAssetLibrary.load_blueprint_class(bp_path)
    new_actor = actor_subsystem.spawn_actor_from_class(bp_class, location, rotation)
    print("Spawnato!")
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
    camera_actor = actor_subsystem.spawn_actor_from_class(camera_class, camera_location, rotation)

    #imposta parametri di fuoco
    camera_component = camera_actor.get_component_by_class(unreal.CameraComponent.static_class())
    camera_component.set_editor_property("field_of_view",75.0)
    camera_component.set_editor_property("aspect_ratio", 1.5)

    if camera_actor:
        camera_actor.set_actor_label("ActorCam")
    else:
        unreal.log_warning("Spawn Actor fallito")

    return camera_actor

def despawn_camera_actor(actor_camera_obj):
    despawn_metahuman(actor_camera_obj)




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
    '''
    actor = spawn_metahuman("Bernice")
    camera_actor = spawn_camera_actor(actor)


    print("Fine Main!")

