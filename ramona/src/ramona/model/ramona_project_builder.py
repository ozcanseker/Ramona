import json
import logging
from pathlib import Path
from typing import Any

from ramona.model.classes.RamonaProject import Model, RamonaProject
from ramona.model.resolver import ResolveContext, resolve_jinja_yaml
from ramona.utils import constants
from ramona.utils.file_handler import get_abs_path_and_validate_if_exists, get_abs_ramona_config_path, get_all_yaml_files_in_dir_and_sub_dirs, read_file, read_yaml_from_filepath

logger=logging.getLogger(constants.LOGGER_NAME)

def build_ramona_project(ramona_project_config_path : str | Path):
    ramona_project: RamonaProject = load_ramona_project_config(ramona_project_config_path)

    register_all_models(ramona_project)
    register_all_objects(ramona_project)
    # validate_objects(ramona_project)


def load_ramona_project_config(ramona_project_config_path: str | Path):
    ramona_project_abs_path: Path=get_abs_ramona_config_path(ramona_project_config_path)
    ramona_project: RamonaProject = RamonaProject(ramona_project_abs_path)
    logger.debug(f"initalized ramona project as: \n{ramona_project}")

    # Set up variables so we can resolve the arguments used in 
    ramona_project_yaml_string=read_file(ramona_project_abs_path)
    resolve_context=ResolveContext()

    resolved_project_yaml_dict=resolve_jinja_yaml(ramona_project_yaml_string, resolve_context)
    ramona_project.set_project_config(resolved_project_yaml_dict)
    logger.debug(f"Finished initalizing ramona project as: \n{ramona_project}")

    return ramona_project


def register_all_models(ramona_project: RamonaProject):
    all_model_config_file_paths_abs=get_all_models_config_files(ramona_project)

    for model_abs_path in all_model_config_file_paths_abs:
        model_yaml_string=read_file(model_abs_path)

        if not model_yaml_string:
            continue

        resolve_context=ResolveContext(ramona_project=ramona_project)
        resolved_model= resolve_jinja_yaml( model_yaml_string,resolve_context)

        # Register model
        model: Model = Model(model_abs_path)
        model.model_config=resolved_model
        model.all_yaml_config_paths_in_model=get_all_yaml_files_in_dir_and_sub_dirs(model.model_folder)

        ramona_project.register_model(model)
        logger.info(f"Registered model: {model.id}")
        logger.debug(f"Registered model as: \n{model}")


def get_all_models_config_files(ramona_project: RamonaProject) -> list[Path]:
    models_dir=get_abs_path_and_validate_if_exists(
        ramona_project.get_from_project_config(constants.project_config_keys.MODELS_DIR),
        ramona_project.project_folder)
    
    all_model_dirs:list[Path]=[]

    for f in models_dir.rglob(constants.filenames.MODEL_CONFIG):
        all_model_dirs.append(f)

    # Also validate that there are not model_config.yaml inside another model_config.yaml
    for f in all_model_dirs:
        for f2 in all_model_dirs:
            if f is not f2 and f.parent in f2.parents:
                raise Exception("every model should have only one model_config")

    return all_model_dirs


def register_all_objects(ramona_project: RamonaProject):
    for model in ramona_project.get_models_as_list():
        for yaml_file_path in model.all_yaml_config_paths_in_model:            
            resolved_objects: dict[str, Any]=create_squashed_template_configs(yaml_file_path, model, ramona_project)

            logger.debug(f"Retrieved the following objects from yaml file:\n"
                         f"{yaml_file_path}\n"
                         f"{json.dumps(resolved_objects, indent=4, sort_keys=True)}")

            if not resolved_objects:
                continue


def create_squashed_template_configs(yaml_file_path: Path, model: Model, ramona_project: RamonaProject):
    yaml_file_contents=read_file(yaml_file_path)

    if not yaml_file_path:
        return []

    # Check if file has objects, otherwise no need because output of file is objects
    if constants.model_keys.OBJECTS not in yaml_file_contents:
        return []

    parent_yaml_files_sorted = parent_yaml_files_sorted_highest_first(yaml_file_path, model)
    final_config=dict(ramona_project.project_config) | dict(model.model_config)

    for parent_yaml_file in parent_yaml_files_sorted:
        parent_yaml_content=read_file(parent_yaml_file)

        if not parent_yaml_content:
            continue

        resolved_dict = resolve_jinja_yaml(
            parent_yaml_content,
            ResolveContext(
                ramona_project=ramona_project,
                model=model,
                scope=final_config
            )
        )

        final_config= final_config | resolved_dict

    resolved_yaml_file_with_objects=resolve_jinja_yaml(
        read_file(yaml_file_path),
        ResolveContext(
            ramona_project=ramona_project,
            model=model,
            scope=final_config
        )
    )

    # also add the parents keys of the yaml files to the final_config
    resolved_yaml_file_without_objects = dict(resolved_yaml_file_with_objects)
    resolved_yaml_file_without_objects.pop(constants.model_keys.OBJECTS)
    final_config = final_config | resolved_yaml_file_without_objects

    # Generate all object configs
    all_object_configs=[]

    for object in resolved_yaml_file_with_objects[constants.model_keys.OBJECTS]:
        object = final_config | object 
        all_object_configs.append(object)

    return all_object_configs
    


def parent_yaml_files_sorted_highest_first(yaml_file_path: Path, model: Model):
    if yaml_file_path == model.model_config_file_path:
        return []

    # First remove all child yaml paths
    parent_yaml_files=[ parent for parent in model.all_yaml_config_paths_in_model if parent.parent in yaml_file_path.parents ]

    parent_yaml_files.remove(model.model_config_file_path)

    # Also remove same level yaml paths because those are not parent
    parent_yaml_files=[ path for path in parent_yaml_files if yaml_file_path.parent != path.parent ]

    parent_yaml_files.sort(
        key = lambda item : (len(item.parents), item.name)
    )

    return parent_yaml_files
