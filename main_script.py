import unreal

# Ottieni il sottosistema per la manipolazione degli attori in editor
actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


all_elements = actor_subsystem.get_all_level_actors()
real_actor = []
for actor in all_elements:
    if "Bryan" in actor.get_name():
        real_actor.append(actor)
        print(actor.get_name() + "Added")


real_actor[0].call_method("StartFromPython")
print("End Call")

#unreal.AssetToolsHelpers.get_asset_tools().create_asset()