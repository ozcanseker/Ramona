import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, pass_context
from ramona.model.classes.RamonaProject import Object, RamonaProject
from ramona.utils import constants
from ramona.utils.file_handler import append_file, clean_folders, get_abs_path_and_validate_if_exists, write_file


logger=logging.getLogger(__name__)


def generate_templates(ramona_project: RamonaProject):
    # Create jinja2 env
    logger.info("Prepare generation of objects...")
    templates_dir=get_abs_path_and_validate_if_exists(
        ramona_project.project_config[constants.project_config_keys.TEMPLATES_DIR],
        ramona_project.project_folder)
    jinja2_env = create_jinja2_env(templates_dir)
    logger.debug(f"Jinja2 env initalized at folder {templates_dir}")

    logger.info("Cleaning folders to be used...")
    clean_folders_to_be_used(ramona_project)

    logger.info("Start generation...")
    for object in ramona_project.get_all_objects_as_list():
        if not constants.object_keys.TEMPLATE_CONFIG in  object.object_config:
            continue

        for template_config in object.object_config[constants.object_keys.TEMPLATE_CONFIG]:
            if constants.template_keys.TEMPLATE in template_config:
                generate_based_on_template(object.clone() | template_config, ramona_project, jinja2_env)

            if constants.template_keys.COPY_FROM in template_config:
                copy_over_file(object.clone() | template_config)
                

def copy_over_file(object: Object):
    copy_from = Path(object[constants.template_keys.COPY_FROM])
    output_path=""

    # The output dir
    if constants.generic_keys.OUTPUT_DIR in object:
        output_path = Path(object[constants.object_keys.OUTPUT_DIR])
    else:
        return

    if not copy_from.exists():
        raise Exception(
            f"copy from generation failed: {copy_from} does not exist"
        )

    output_path.mkdir(parents=True, exist_ok=True)

    if copy_from.is_dir():
        for item in copy_from.iterdir():
            item.copy_into(
                output_path,
                preserve_metadata=True
            )
    else:
        copy_from.copy(
            output_path / copy_from.name,
            preserve_metadata=True
        )


def generate_based_on_template(object: Object, ramona_project: RamonaProject, jinja2_env: Environment):
    append=object[constants.template_keys.APPEND] if  constants.template_keys.APPEND in object else False

    # Get the output
    logger.debug(f"Generating {object.id} with template: {object[constants.template_keys.TEMPLATE]}")
    template = jinja2_env.get_template(object[constants.template_keys.TEMPLATE])
    logger.debug(f"generating with object\n{object}")

    file_path: Path=get_full_file_location(object)
    output = template.render(
                    object=object, 
                    project=ramona_project, 
                    template_config=object, 
                    constants=constants, 
                    first_object_to_generate=not file_path.exists()
                )
    
    if append:
        append_file(file_path, output)
    else: 
        write_file(file_path, output)
    

def create_jinja2_env(tempalte_location: Path) -> Environment:
    env = Environment(
        loader=FileSystemLoader(tempalte_location),
        lstrip_blocks=True,
        trim_blocks=True
    )

    env.globals["to_relative_path"] = to_relative_path
    env.globals["get_file_name"] = get_file_name

    return env


def clean_folders_to_be_used(ramona_project: RamonaProject):
    folders_to_be_cleaned=set()

    for object in ramona_project.get_all_objects_as_list(): 
        if constants.object_keys.OUTPUT_DIR in object.object_config: 
            folders_to_be_cleaned.add(object.object_config[constants.object_keys.OUTPUT_DIR])

    if constants.project_config_keys.GENERATED_PATHS in ramona_project.project_config:
        for generated_paths in ramona_project.get_from_project_config(constants.project_config_keys.GENERATED_PATHS):
            folders_to_be_cleaned.add(generated_paths)

    clean_folders(folders_to_be_cleaned)


def get_full_file_location(object: Object):
    output_dir=None
    
    # The output dir 
    if constants.generic_keys.OUTPUT_DIR in object:
        output_dir=Path(object[constants.object_keys.OUTPUT_DIR])
    else:
        return

    # Name of the to be written file
    file_name=get_file_name(object)

    # Get the suffix after templatename and before jinja2, so example.sql.jinja -> .sql
    file_extension=Path(object[constants.template_keys.TEMPLATE]).suffixes[0]

    # Full path for to be written file:
    return Path(f"{output_dir.joinpath(file_name)}{file_extension}")


@pass_context
def to_relative_path(context, file_path):
    proj: RamonaProject = context["project"]
    return Path(file_path).relative_to(proj.project_folder).as_posix()


def get_file_name(object):
    file_name = ""

    if constants.object_keys.FILENAME in object:
        file_name=object[constants.object_keys.FILENAME]
    elif constants.object_keys.NAME in object:
        file_name=object[constants.object_keys.NAME]
    elif constants.object_keys.ID in object:
        file_name=object[constants.object_keys.ID]
    else:
        raise Exception("There is no name or id in the model_config")

    return file_name