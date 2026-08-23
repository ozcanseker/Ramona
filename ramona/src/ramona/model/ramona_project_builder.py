import re
import logging
from typing import Any
from pathlib import Path

from ramona.model.classes.RamonaProject import Model, Object, RamonaProject
from ramona.model.reference_resolver import resolve_references
from ramona.model.resolver import ResolveContext, resolve_jinja_yaml
from ramona.utils import constants
from ramona.utils.file_handler import get_abs_path, get_abs_path_and_validate_if_exists, get_abs_ramona_config_path, get_all_yaml_files_in_dir_and_sub_dirs, read_file, read_yaml_from_filepath, read_yaml_from_string

logger=logging.getLogger(__name__)

def build_ramona_project(ramona_project_config_path : str | Path):
    ramona_project: RamonaProject = load_ramona_project_config(ramona_project_config_path)

    # Process models
    logger.info("Registering models...")
    register_all_models(ramona_project)

    # Process objects
    logger.info("Registering objects...")
    register_all_objects(ramona_project)

    logger.info("Resolve references of objects...")
    resolve_references(ramona_project)
    register_child_objects_of_objects(ramona_project)
    logger.debug("Finished processing all objects:")
    logger.debug(ramona_project.get_all_objects_as_list())

    # Validate models
    logger.info("Validating objects...")
    validate_and_correct_project(ramona_project)

    return ramona_project


def validate_and_correct_project(ramona_project: RamonaProject):
    _validate_and_correct_project(ramona_project)
    
    for object in ramona_project.get_all_objects_as_list():
        # Pre correct models checks
        check_if_object_has_required_keys(object, ramona_project)

        # Correct models
        correct_file_paths_to_abs(object, ramona_project, constants.object_keys.OUTPUT_DIR)

        # after correct models checks
        check_if_output_folder_is_valid(object, ramona_project)

        if constants.object_keys.TEMPLATE_CONFIG in object:
            for template_config in object[constants.object_keys.TEMPLATE_CONFIG]:
                validate_and_correct_template_config(template_config, object, ramona_project)


def validate_and_correct_template_config(template_config: dict, object: Object, ramona_project: RamonaProject):
    correct_file_paths_to_abs(template_config, ramona_project, constants.generic_keys.OUTPUT_DIR)
    correct_file_paths_to_abs(template_config, ramona_project, constants.template_keys.COPY_FROM)

    check_if_output_folder_is_valid(template_config, ramona_project)

    if constants.generic_keys.OUTPUT_DIR not in template_config and constants.generic_keys.OUTPUT_DIR not in object:
        raise Exception("Need to at lease have one output_dir key in the object or template_config")


def _validate_and_correct_project(ramona_project: RamonaProject):
    # Fix generated paths, and validate
    if not constants.project_config_keys.GENERATED_PATHS in ramona_project.project_config:
        raise Exception("There is no generated paths in the project config")

    if not isinstance(ramona_project.project_config[constants.project_config_keys.GENERATED_PATHS], list):
        raise Exception("generated paths is not a list")

    abs_generated_paths=[]
    for path in ramona_project.project_config[constants.project_config_keys.GENERATED_PATHS]:
        abs_path=get_abs_path(path, ramona_project.project_folder)

        if ramona_project.project_folder not in abs_path.parents:
            raise Exception("Generated pathss outside of project folder")

        abs_generated_paths.append(abs_path)

    ramona_project.project_config[constants.project_config_keys.GENERATED_PATHS]=abs_generated_paths

def check_if_object_has_required_keys(object: Object, ramona_project: RamonaProject):
    if constants.object_keys.ID not in object.object_config:
        raise Exception("object has no id")


def correct_file_paths_to_abs(to_correct: Object | dict, ramona_project: RamonaProject, key: str):
    if key in to_correct:
        to_correct[key]=get_abs_path(
            to_correct[key],
            ramona_project.project_folder
        )


def check_if_output_folder_is_valid(to_check: Object | dict, ramona_project: RamonaProject):
    if constants.generic_keys.OUTPUT_DIR not in to_check:
        return

    is_in_generated_path=False
    to_check_output_dir=Path(to_check[constants.generic_keys.OUTPUT_DIR])

    for generated_path in ramona_project.project_config[constants.project_config_keys.GENERATED_PATHS]:
        if generated_path in to_check_output_dir.parents or generated_path == to_check_output_dir:
            is_in_generated_path=True

    if not is_in_generated_path:
        raise Exception(f"output dir {to_check[constants.generic_keys.OUTPUT_DIR]} outside of generated_path")


def register_child_objects_of_objects(ramona_project: RamonaProject):
    # first project_objest
    all_model_objects=ramona_project.get_all_model_objects_as_list()

    for object in ramona_project.objects.values():
        object.object_config[constants.object_keys.CHILD_OBJECTS]=all_model_objects

    # assign the child object to object in models correctly
    for model in ramona_project.get_models_as_list():
        for object in model.get_all_objects_as_list():
            child_yaml_files=get_child_yaml_files(object.object_config_file_path, list(model.all_yaml_config_paths_in_model))
            objects_from_child_yaml_files=get_object_from_child_yaml_files(child_yaml_files, model)
            object.object_config[constants.object_keys.CHILD_OBJECTS]=objects_from_child_yaml_files


def get_object_from_child_yaml_files(child_yaml_files: list[Path], model: Model):
    all_objects=[]

    for yaml_file in child_yaml_files:
        all_objects = all_objects + model.get_objects_for_path(yaml_file)

    return all_objects


def get_child_yaml_files(yaml_file: Path, list_of_yaml_files: list[Path]):
    return_list = list(list_of_yaml_files)
    return_list = [ childpath for childpath in return_list if yaml_file.parent in childpath.parents ]
    return_list = [ childpath for childpath in return_list if yaml_file.parent != childpath.parent ]
    return return_list

def load_ramona_project_config(ramona_project_config_path: str | Path):
    ramona_project_abs_path: Path=get_abs_ramona_config_path(ramona_project_config_path)
    ramona_project: RamonaProject = RamonaProject(ramona_project_abs_path)
    logger.debug(f"initalized ramona project as: \n{ramona_project}")

    # Set up variables so we can resolve the arguments used in 
    ramona_project_yaml_string=read_file_combined_with_includes(ramona_project_abs_path, ramona_project.project_folder)
    resolve_context=ResolveContext()

    resolved_project_yaml_dict=resolve_jinja_yaml(ramona_project_yaml_string, resolve_context)
    ramona_project.set_project_config(resolved_project_yaml_dict)
    logger.debug(f"Finished initalizing ramona project as: \n{ramona_project}")

    return ramona_project


def register_all_models(ramona_project: RamonaProject):
    all_model_config_file_paths_abs=get_all_models_config_files(ramona_project)

    for model_abs_path in all_model_config_file_paths_abs:
        model_yaml_string=read_file_combined_with_includes(model_abs_path, ramona_project.project_folder)

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

    for model_config_file_name in constants.filenames.MODEL_CONFIG_NAMES:
        for f in models_dir.rglob(model_config_file_name):
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

            if not resolved_objects:
                continue

            for resolved_object in resolved_objects:
                object = Object(yaml_file_path, resolved_object)
                model.register_object(object)
                logger.debug(f"Registered the following object:\n{object}")

    if constants.model_keys.OBJECTS in ramona_project.project_config:
        project_objects=ramona_project.get_from_project_config(constants.model_keys.OBJECTS)
        final_config=dict(ramona_project.project_config)
        final_config.pop(constants.model_keys.OBJECTS)

        for object in project_objects:
            object_config = final_config | object
            object = Object(ramona_project.project_config_file_path, object_config)
            ramona_project.register_object(object)
            logger.debug(f"Registered the following object:\n{object}")

        

def create_squashed_template_configs(yaml_file_path: Path, model: Model, ramona_project: RamonaProject):
    if not yaml_file_path:
        return []

    yaml_file_contents=read_file_combined_with_includes(yaml_file_path, ramona_project.project_folder)

    # Check if file has objects, otherwise no need because output of file is objects
    if not re.search(rf"^[\t ]*{constants.model_keys.OBJECTS}[\t ]*:", yaml_file_contents, re.MULTILINE):
        return []

    parent_yaml_files_sorted = parent_yaml_files_sorted_highest_first(yaml_file_path, model)
    final_config=dict(ramona_project.project_config) | dict(model.model_config)

    for parent_yaml_file in parent_yaml_files_sorted:
        parent_yaml_content=read_file_combined_with_includes(parent_yaml_file, ramona_project.project_folder)

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
        read_file_combined_with_includes(yaml_file_path, ramona_project.project_folder),
        ResolveContext(
            ramona_project=ramona_project,
            model=model,
            scope=final_config
        )
    )

    # also add the parents keys of the yaml files to the final_config
    final_config = final_config | dict(resolved_yaml_file_with_objects)
    final_config.pop(constants.model_keys.OBJECTS)

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


def read_file_combined_with_includes(file_path: Path, base_dir: Path = None):
    file_content = read_file(file_path)

    pattern = rf"""
    ^(
        {constants.generic_keys.INCLUDE}\s*:\s*\n
        (?:^[ \t]+-.*(?:\n|$))*
    )
    """

    # Extract include part
    match = re.search(
        pattern,
        file_content,
        re.MULTILINE | re.VERBOSE,
    )

    if not match:
        return file_content

    include_yaml = read_yaml_from_string(match.group(1))

    final_string = file_content

    for yaml_file in include_yaml[constants.generic_keys.INCLUDE]:
        abs_path = get_abs_path(yaml_file, base_dir)
        include_contents=read_file(Path(abs_path))

        final_string = f"{final_string}\n\n{include_contents}"

    return final_string
