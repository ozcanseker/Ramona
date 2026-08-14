import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from ramona.model.classes.RamonaProject import Object, RamonaProject
from ramona.utils import constants
from ramona.utils.file_handler import clean_folders, get_abs_path, get_abs_path_and_validate_if_exists, write_file


logger=logging.getLogger(__name__)


def generate_templates(ramona_project: RamonaProject):
    logger.info("Start generation of objects...")

    # Create jinja2 env
    templates_dir=get_abs_path_and_validate_if_exists(
        ramona_project.project_config[constants.project_config_keys.TEMPLATES_DIR],
        ramona_project.project_folder)
    jinja2_env = create_jinja2_env(templates_dir)
    logger.info(f"Jinja2 env initalized at folder {templates_dir}")

    logger.info("Cleaning folders to be used...")
    clean_folders_to_be_used(ramona_project)

    logger.info("Start generation...")
    for object in ramona_project.get_all_objects_as_list():
        if not constants.object_keys.GENERATION_CONFIG in  object.object_config:
            continue

        for generation_config in object.object_config[constants.object_keys.GENERATION_CONFIG]:
            if constants.generation_keys.TEMPLATE:
                generate_based_on_template(object, generation_config, jinja2_env)


def generate_based_on_template(object: Object, generation_config, jinja2_env: Environment):
    # Get the output
    template = jinja2_env.get_template(generation_config[constants.generation_keys.TEMPLATE])
    output = template.render(object=object)

    # The output dir 
    output_dir=Path(object.object_config[constants.object_keys.OUTPUT_DIR])

    # Name of the to be written file
    file_name=""

    if constants.object_keys.FILENAME in object.object_config:
        file_name=object.object_config[constants.object_keys.FILENAME]
    elif constants.object_keys.NAME in object.object_config:
        file_name=object.object_config[constants.object_keys.NAME]
    elif constants.object_keys.ID in object.object_config:
        file_name=object.object_config[constants.object_keys.ID]
    else:
        raise Exception("There is no name or id in the model_config")

    # Get the suffix after templatename and before jinja2, so example.sql.jinja -> .sql
    file_extension=Path(template.name).with_suffix("").suffix

    # Full path for to be written file:
    file_path=Path(f"{output_dir.joinpath(file_name)}{file_extension}")

    write_file(file_path , output)
    

def create_jinja2_env(tempalte_location: Path) -> Environment:
    env = Environment(
        loader=FileSystemLoader(tempalte_location),
        lstrip_blocks=True,
        trim_blocks=True
    )

    return env

def clean_folders_to_be_used(ramona_project: RamonaProject):
    folders_to_be_cleaned=set()

    for object in ramona_project.get_all_objects_as_list(): 
        if constants.object_keys.OUTPUT_DIR in object.object_config: 
            folders_to_be_cleaned.add(object.object_config[constants.object_keys.OUTPUT_DIR])

    if constants.project_config_keys.ALWAYS_CLEAN in ramona_project.project_config:
        for always_to_be_cleaned_path in ramona_project.get_from_project_config(constants.project_config_keys.ALWAYS_CLEAN):
            folders_to_be_cleaned.add(always_to_be_cleaned_path)

    clean_folders(folders_to_be_cleaned)