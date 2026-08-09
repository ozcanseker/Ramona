# Python libs
import json
from pathlib import Path

from ramona.generator.generator import generate_templates
from ramona.model.model_loader import get_model_configs
from ramona.model.resolver import ResolveContext, resolve
from ramona.singletons import project_config
from ramona.utils import constants
from ramona.utils.file_handler import get_abs_path_and_validate_if_exists, read_yaml
from .singletons import application_arguments


def main():
    # Get the location of the generator file and the parent dir
    project_config_abs_path:Path = get_abs_generator_config_path(application_arguments.get().project_config_path)

    # # Initalize the singleton for generator file config
    setup_project_singleton(project_config_abs_path)

    # # Get all template config, aka everything that has to be generated
    list_of_model_configs=get_model_configs()

    # for model_config in list_of_model_configs:
    #     # print(template_config)
    #     print(json.dumps (model_config, indent=4, sort_keys=True))
    #     # generate all templates

    if application_arguments.get().command == constants.commands.GENERATE:
        generate_templates(list_of_model_configs)
    # elif application_arguments.get().command == constants.MODELCHECK_COMMAND:
    #     raise NotImplementedError("that command is not implemented")
    else:
        raise NotImplementedError("that command is not implemented")


def get_abs_generator_config_path(project_config_path_str: str):
    try:
        project_config_path: Path=get_abs_path_and_validate_if_exists(project_config_path_str)

        if project_config_path.is_file():
            return project_config_path

        raise Exception
    except Exception as e:
        raise Exception(f"argument for project_config_path is not valid, {project_config_path_str} does not point to a valid file.")


def setup_project_singleton(project_config_abs_path: Path):
    project_config.set_path(project_config_abs_path)
    # The working dir is the dir of the config file. Can change it so later an argument can be given to change this
    # This means all relative paths in projects, should be assuming this as working dir
    project_config.set_dir(project_config_abs_path.parent)

    # Set up config
    project_config_dict=read_yaml(project_config_abs_path)

    # resolve the project_config
    project_config_dict=resolve(project_config_dict, ResolveContext(project=project_config_dict))
    project_config.set_config(project_config_dict)

    print("Project_config: ", json.dumps (project_config_dict, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()