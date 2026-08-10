from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from ramona.singletons import project_config
from ramona.utils import constants
from ramona.utils.file_handler import clean_folders, get_abs_path, get_abs_path_and_validate_if_exists, write_file


def generate_templates(list_of_model_configs):
    templates_dir=get_abs_path_and_validate_if_exists(
        project_config.get().project_config[constants.project_config_keys.TEMPLATES_DIR],
        project_config.get().project_abs_dir)

    jinja2_env = create_jinja2_env(templates_dir)

    clean_folders_to_be_used(list_of_model_configs)

    for model in list_of_model_configs:
        for generation_config in model[constants.model_keys.GENERATION_CONFIG]:
            if constants.GENERATION_CONFIG_TEMPLATE_KEY:
                generate_based_on_template(model, generation_config, jinja2_env)


def clean_folders_to_be_used(list_of_model_configs):
    folders_to_be_cleaned=set()

    for model in list_of_model_configs:
            if not constants.model_keys.OUTPUT_DIR in model:
                continue
    
            output_dir=Path(model[constants.model_keys.OUTPUT_DIR])
    
            if not output_dir.exists() or not output_dir.is_dir():
                continue
    
            folders_to_be_cleaned.add(output_dir)

    if constants.project_config_keys.ALWAYS_CLEAN in project_config.get().project_config:
        for always_to_be_cleaned_path in project_config.get_key(constants.project_config_keys.ALWAYS_CLEAN):
            abs_path=get_abs_path(always_to_be_cleaned_path, project_config.get().project_abs_dir)
            folders_to_be_cleaned.add(abs_path)

    clean_folders(folders_to_be_cleaned)


def generate_based_on_template(model, generation_config, jinja2_env: Environment):
    # Get the output
    template = jinja2_env.get_template(generation_config[constants.GENERATION_CONFIG_TEMPLATE_KEY])
    output = template.render(model=model)

    # The output dir 
    output_dir=Path(model[constants.model_keys.OUTPUT_DIR])

    # Name of the to be written file
    file_name=""

    if constants.model_keys.FILENAME in model:
        file_name=model[constants.model_keys.FILENAME]
    elif constants.model_keys.NAME in model:
        file_name=model[constants.model_keys.NAME]
    elif constants.model_keys.ID in model:
        file_name=model[constants.model_keys.ID]
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