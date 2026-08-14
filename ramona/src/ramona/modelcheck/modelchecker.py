
import logging

from ramona.model.classes.RamonaProject import RamonaProject
from rich.console import Console

from pathlib import Path
from types import ModuleType

from ramona.modelcheck.classes.CheckResult import CheckResult, CheckStatus
from ramona.modelcheck.classes.ModelCheckConfig import ModelCheckConfig
from ramona.utils import constants
from ramona.utils.file_handler import get_abs_path_and_validate_if_exists, load_module
from ramona.modelcheck.classes.ModelCheckClass import ModelCheck

logger=logging.getLogger(__name__)

def run_modelchecks(ramona_project: RamonaProject):
    logger.info("Prepare modelcheck for objects...")

    
    logger.info("Retrieve modelchecks folder...")
    modelchecks_dir:Path=get_modelchecks_folder(ramona_project)

    logger.info("Load modelchecks...")
    all_checks = load_checks(modelchecks_dir)

    logger.info("Running modelchecks...")
    _run_modelchecks(all_checks, ramona_project)

    logger.info("Printing modelchecks...")
    print_results(all_checks)


def _run_modelchecks(modelchecks: list[ModelCheck], ramona_project: RamonaProject):
    for check in modelchecks:
        for object in ramona_project.get_all_objects_as_list():
            result = check.run(object)
            check.results.append(result)
            

def load_registered_checks( module: ModuleType ) -> list[ModelCheck]:
    checks: list[ModelCheck] = []

    for value in vars(module).values():
        modelcheck = getattr(value, "__modelcheck__", None)

        if modelcheck is not None:
            logger.debug(f"Found modelcheck named: {modelcheck.name}")
            modelcheck.filepath=Path(module.__file__)
            checks.append(modelcheck)

    return checks


def get_modelchecks_folder(ramona_project: RamonaProject) -> Path:
    if not constants.project_config_keys.MODELCHECKS in  ramona_project.project_config:
        raise Exception("project config requires modelcheck key")

    rel_folder = ramona_project.project_config[constants.project_config_keys.MODELCHECKS]
    return get_abs_path_and_validate_if_exists(rel_folder, ramona_project.project_folder)


def load_checks(modelchecks_dir: Path ):
    all_checks : list[ModelCheck] = []

    for file in modelchecks_dir.rglob("*.py"):
        if file.name == "__init__.py":
            continue

        logger.debug(f"Found python module at {file}")
        module = load_module(f"{constants.FileLoader.MODULE_PREFIX}{file.stem}", file)
        modelchecks = load_registered_checks(module)

        logger.debug(f"check if global config")
        global_modelcheck_config = getattr(module, "config", ModelCheckConfig())

        for modelcheck in modelchecks:
            apply_config_to_modelcheck(modelcheck, global_modelcheck_config)

        all_checks.extend(modelchecks)

    return all_checks



def apply_config_to_modelcheck( modelcheck: ModelCheck, config: ModelCheckConfig) -> ModelCheck:
    if modelcheck.severity is None:
        modelcheck.severity = config.severity

    modelcheck.conditions = [
        *config.conditions,
        *modelcheck.conditions,
    ]

    return modelcheck


def print_results(modelchecks: list[ModelCheck]):
    console = Console()
    modelchecks.sort(key=lambda modelcheck: (modelcheck.filepath, modelcheck.name) )

    failed=0
    warnings=0
    success=0
    skipped=0
    current_module=Path("")

    console.print("[purple]Ramona Model Checks[/purple]")
    print("")
    print("─"*35)

    for modelcheck in modelchecks:
        if current_module != modelcheck.filepath:
            current_module=Path(modelcheck.filepath)
            print(f"Module file: {modelcheck.filepath}")

        print(f"  Modelcheck name: {modelcheck.name}")
        if modelcheck.description:
            print(f"  Description: {modelcheck.description}")

        
        print(f"  Model results:")
        for result in modelcheck.results:
            color=""
            color_closer=""
            symbol="?"

            if result.status in CheckStatus.PASSED:
                success += 1
                color="[green]"
                color_closer="[/green]"
                symbol="✓"
            elif result.status in CheckStatus.FAILED:
                if modelcheck.severity == "error":
                    failed += 1
                    color="[red]"
                    color_closer="[/red]"
                    symbol="✗"
                elif modelcheck.severity == "warning":
                    warnings += 1
                    color="[yellow]"
                    color_closer="[/yellow]"
                    symbol="⚠"
            elif result.status in CheckStatus.SKIPPED:
                skipped += 1
                color="[dim]"
                color_closer="[/dim]"
                symbol="-"

            if "id" in result.object:            
                console.print(f"{color}    {symbol} Model: {result.object["id"]}{color_closer}")

            if result.message and result.status in CheckStatus.FAILED:
                console.print(f"{color}        Error message: {result.message}{color_closer}")

            console.print(f"{color}        Model filepath: {result.object.object_config_file_path}{color_closer}")
        
        print("")


    print("─"*35)
    print("Total results:")
    print(f"  Success:  {success}")
    print(f"  Failed:   {failed}")
    print(f"  Warnings: {warnings}")
    print(f"  Skipped:  {skipped}")
