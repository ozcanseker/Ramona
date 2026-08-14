# Python libs
import json
import logging
from pathlib import Path

from ramona.model.classes.RamonaProject import RamonaProject
from ramona.model.ramona_project_builder import build_ramona_project
from ramona.utils import constants
from ramona.utils.file_handler import get_abs_ramona_config_path
from ramona.utils.classes.ApplicationArguments import ApplicationArguments


logger=logging.getLogger(constants.LOGGER_NAME)


def main():
    # Get app arguments
    application_arguments: ApplicationArguments = get_app_arguments()

    # Inialize app
    initalize_ramona_app(application_arguments.ramona_config_path)

    # Build the ramona project
    logger.info("Building Ramona project...")
    ramona_project: RamonaProject = build_ramona_project(application_arguments.ramona_config_path)

    # Get all the objects in all the models
    # list_of_model_configs=get_model_configs()
    # print(list_of_model_configs)

    # for model_config in list_of_model_configs:
    #     # print(template_config)
    #     print(json.dumps (model_config, indent=4, sort_keys=True))
    #     # generate all templates

    # if application_arguments.get().command == constants.commands.GENERATE:
    #     generate_templates(list_of_model_configs)
    # elif application_arguments.get().command == constants.commands.MODELCHECK:
    #     run_modelchecks(list_of_model_configs)
    # else:
    #     raise NotImplementedError("that command is not implemented")


def get_app_arguments() -> ApplicationArguments:
    # Get app arguments
    application_arguments: ApplicationArguments=ApplicationArguments().get_application_arguments()

    # Do a quick check if the project file is valid
    get_abs_ramona_config_path(application_arguments.ramona_config_path)

    return application_arguments


def initalize_ramona_app(project_config_location: str | Path) -> None:
    log_location = get_abs_ramona_config_path(project_config_location)
    log_location = log_location.parent.joinpath(constants.LOG_LOCATION)

    #logger
    initalize_logger(log_location)
    logger.debug("-----Start Ramona Run------")
    logger.info("initalizing project...")


def initalize_logger(log_location: Path):
    log_location.parent.mkdir(parents=True, exist_ok=True)

    # Remember whether this is a new log file
    log_file_exists = log_location.exists()

    logger = logging.getLogger(constants.LOGGER_NAME)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return
    
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # create file handler which logs even debug messages
    fh = logging.FileHandler(log_location)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    if log_file_exists:
        fh.stream.write("\n\n")
        fh.flush()
        # TODO REMOVE
        print(log_location)
        log_location.write_text("")


if __name__ == "__main__":
    main()