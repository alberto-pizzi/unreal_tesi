import unreal
from config import *

def get_rendering_settings_path(setting_name:str):
    full_path = RENDERING_SETTINGS_PATH + setting_name + "." + setting_name
    return full_path

def get_ls_path(ls_name:str):
    full_path = LS_BASE_PATH + ls_name + "." + ls_name
    return full_path

def get_level_path(level_name:str):
    full_path = LEVELS_PATH + level_name + "." + level_name
    return full_path

def get_queue_path(queue_name:str):
    full_path = QUEUES_PATH + queue_name + "." + queue_name
    return full_path

def clear_all_mrq():
    subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
    queue = subsystem.get_queue()
    queue.delete_all_jobs()

def load_queue(queue_name:str):
    movie_queue = unreal.load_asset(get_queue_path(queue_name))
    return movie_queue


def import_ls_into_mrq(ls_name:str,queue_name:str):
    mrq = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)

    if not ls_name:
        unreal.log_error(f"Unable to load level sequence : {ls_name}")
    else:
        #queue = mrq.get_queue()
        queue = load_queue(queue_name)
        if queue and isinstance(queue, unreal.MoviePipelineQueue):
            job = queue.allocate_new_job(unreal.MoviePipelineExecutorJob)

            job.map = unreal.SoftObjectPath(get_level_path(LEVEL_NAME))
            job.sequence = unreal.SoftObjectPath(get_ls_path(ls_name))
            job.job_name = ls_name

            preset = unreal.load_object(None, get_rendering_settings_path(RENDERING_SETTINGS_NAME))
            job.set_configuration(preset)

            unreal.EditorAssetLibrary.save_loaded_asset(queue)

        else:
            unreal.log_error(f"Unable to load queue: {queue_name}")

def get_current_queue():
    subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
    # take current queue
    queue = subsystem.get_queue()
    return queue


if __name__ == "__main__":
    print("Im rendering")
    #import_ls_into_mrq("SeqVM","RenderingQueue1")
    #queue = create_movie_render_queue_asset("Prova")



    print("Coda: ", QUEUE_NAME)
    print("End main")


