
import control_rig_maps as crm
import a2f_involved_rig_maps as a2f_map

# it is an init function (valid for all iterations)
def create_rig_class_instances():
    rig_instances = {}
    # scroll map by control rig
    for key,rigs in a2f_map.A2F_TO_METAHUMAN.items():
        for rig_name in rigs:
            if rig_name not in rig_instances:
                # if rig has override it uses relative class, else default
                rig_class = crm.RIG_OVERRIDES.get(rig_name, crm.crc.ControlRig)
                # creates class instance
                rig_instances[rig_name] = rig_class(rig_name)

    print("rig instances created!")
    return rig_instances





