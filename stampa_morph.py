import unreal

import unreal


# Metodo ANIM INSTANCE - SEMPRE FUNZIONANTE
def print_face_curves():
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = actor_subsystem.get_selected_level_actors()

    if not actors:
        print("❌ SELEZIONA un MetaHuman nella viewport!")
        return

    actor = actors[0]
    for comp in actor.get_components_by_class(unreal.SkeletalMeshComponent):
        skm_name = comp.skeletal_mesh.get_name() if comp.skeletal_mesh else ""
        if "face" in skm_name.lower():
            anim_inst = comp.get_anim_instance()
            if anim_inst:
                all_curves = anim_inst.get_all_curve_names()
                # FILTRA solo curve facciali
                face_curves = [str(c) for c in all_curves
                               if any(x in str(c).lower() for x in ["arkit", "ctrl_expressions"])]

                print(f"\n🎭 CURVE FACCIALI Bryan ({len(face_curves)}):")
                for curve in sorted(set(face_curves)):
                    print(curve)
                return
    print("❌ Face component non trovato")


print_face_curves()
