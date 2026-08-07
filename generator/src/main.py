# Python libs
import json
from pathlib import Path
import yaml
import re
import ast

# Own libs
import constants
from resolver import ResolveContext, resolve
import singletons.application_arguments as application_arguments
import singletons.workspace_config as workspace_config


def main():
    # Get the location of the generator file and the parent dir
    workspace_proj_config_abs_path:Path = get_abs_generator_config_path(application_arguments.get().workspace_config_path)

    # Initalize the singleton for generator file config
    setup_workplace_singleton(workspace_proj_config_abs_path)

    
    print(json.dumps(workspace_config.get().workspace_config, indent=4, sort_keys=True))

    # all model files
    all_model_config_file: list[Path] = get_all_models_config_files(workspace_config.get().workspace_config)


    # Get all template config, aka everything that has to be generated
    # list_of_template_configs=get_template_configs(list_of_project_dirs, project_config_file_name, generator_config)

    # # for template_config in list_of_template_configs:
    #     # print(template_config)
    #     # print(json.dumps (template_config, indent-4, sort_keys=True)) print(template_config["name"])
    #     # generate all templates

    # generate_templates(generator_config ["generator_config"]["templates_folder"], list_of_template_configs, generator_dir, generator_config)

def get_all_models_config_files(models_dir: Path | str) -> list[Path]:
    models_dir=get_abs_path_of_file_and_validate(
        models_dir[constants.WORKSPACE_CONFIG_MODELS_DIR_KEY], 
        workspace_config.get().workspace_abs_dir
        )
    
    all_model_dirs:list[Path]=[]

    files = models_dir.rglob(constants.MODEL_CONFIG_FILE_NAME)
    for f in files:
        all_model_dirs.append(f)

    # Also validate that there are not model_config.yaml inside another model_config.yaml
    for f in all_model_dirs:
        for f2 in all_model_dirs:
            if f is not f2 and f.parent in f2.parents:
                raise Exception("every model should have only one model_config")

    return all_model_dirs


def setup_workplace_singleton(workspace_proj_config_abs_path: Path):
    workspace_config.set_path(workspace_proj_config_abs_path)
    # The working dir is the dir of the config file. Can change it so later an argument can be given to change this
    # This means all relative paths in projects, should be assuming this as working dir
    workspace_config.set_dir(workspace_proj_config_abs_path.parent)

    # Set up config
    workspace_config_dict=read_yaml(workspace_proj_config_abs_path)
    workspace_config_dict=resolve(workspace_config_dict, ResolveContext(globals=workspace_config_dict["globals"]))
    workspace_config.set_config(workspace_config_dict)

    
def get_abs_generator_config_path(generator_config_path_str: str):
    try:
        generator_config_path: Path=get_abs_path_of_file_and_validate(generator_config_path_str)

        if generator_config_path.is_file():
            return generator_config_path

        raise Exception
    except Exception as e:
        raise Exception(f"argument for generator_config_path is not valid, {generator_config_path_str} does not point to a valid file.")


def get_abs_path_of_file_and_validate(filepath: str|Path, abs_base_dir:Path=None) -> Path:
    # Create copy of object, to not modify original object
    filepath = Path(filepath)

    if not filepath.is_absolute():
        if abs_base_dir:
            filepath=abs_base_dir.joinpath(filepath).resolve()
        else:
            filepath= filepath.resolve()

    if not filepath.exists():
        raise Exception(f"{filepath} file path does not exist")

    return filepath


def read_yaml(filepath):
    with open(filepath, 'r') as file:
        yaml_dict:dict = yaml.safe_load(file)

    # There is always an outer_dict because of how the yaml is constructed, this is never needed, so pop this
    _, inner_dict = yaml_dict.popitem()

    return inner_dict


if __name__ == "__main__":
    main()