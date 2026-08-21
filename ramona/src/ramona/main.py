# Python libs
import sys
import logging
from pathlib import Path
from rich.logging import RichHandler


from ramona.utils import constants
from ramona.generator.generator import generate_templates
from ramona.modelcheck.modelchecker import run_modelchecks
from ramona.model.classes.RamonaProject import RamonaProject
from ramona.utils.file_handler import get_abs_ramona_config_path
from ramona.model.ramona_project_builder import build_ramona_project
from ramona.utils.classes.ApplicationArguments import ApplicationArguments

# GLobal setups
logger=logging.getLogger(__name__)


def run():
    # Get app arguments
    application_arguments: ApplicationArguments = get_app_arguments()

    # Inialize app
    initalize_ramona_app(application_arguments.ramona_config_path)

    # Build the ramona project
    logger.info("Building Ramona project...")
    ramona_project: RamonaProject = build_ramona_project(application_arguments.ramona_config_path)
    logger.info("Finished building ramona project")


    if application_arguments.command == constants.commands.GENERATE:
        logger.info("Start generation...")
        generate_templates(ramona_project)
    elif application_arguments.command == constants.commands.MODELCHECK:
        run_modelchecks(ramona_project)
    else:
        raise NotImplementedError("that command is not implemented")

    logger.info("[italic]Fin.[/italic]")


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
    ch = RichHandler(omit_repeated_times=False, markup=True)
    ch.setLevel(logging.INFO)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    if log_file_exists:
        fh.stream.write("\n\n")
        fh.flush()
        # TODO REMOVE
        log_location.write_text("")


def main():
    try:
        run()
    except Exception as e:
        logger.exception("Ramona terminated unexpectedly")
        sys.exit(1)