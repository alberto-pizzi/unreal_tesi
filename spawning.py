import unreal

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



if __name__ == "__main__":
    print("Inizio Main!")
    actor = select_actor("Bernice")
    if actor:
        print("Attore selezionato")
        despawn_metahuman(actor)
        print("Despawn termianto")
    else:
        print("Non selezionato")

    print("Fine Main!")

