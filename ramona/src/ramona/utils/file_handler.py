import importlib
from pathlib import Path
import shutil
from types import ModuleType

import yaml


def get_abs_ramona_config_path(project_config_path_str: str):
    try:
        project_config_path: Path=get_abs_path_and_validate_is_file(project_config_path_str)

        if project_config_path.is_file():
            return project_config_path

        raise Exception
    except Exception as e:
        raise Exception(f"argument for ramona config path is not valid, {project_config_path_str} does not point to a valid file.")














def get_abs_path_and_validate_is_file(filepath: str|Path, abs_base_dir:Path=None) -> Path:
    filepath: Path = get_abs_path_and_validate_if_exists(filepath, abs_base_dir)

    if not filepath.is_file():
        raise Exception(f"{filepath} is not a file.")

    return filepath


def get_abs_path_and_validate_if_exists(filepath: str|Path, abs_base_dir:Path=None) -> Path:
    filepath: Path = get_abs_path(filepath, abs_base_dir)

    if not filepath.exists():
        raise Exception(f"{filepath} file path does not exist")

    return filepath


def get_abs_path(filepath: str|Path, abs_base_dir:Path=None) -> Path:
    filepath = Path(filepath)

    if not filepath.is_absolute():
        # Resolve based on the given abs base dir
        if abs_base_dir:
            filepath=abs_base_dir.joinpath(filepath)

        filepath= filepath.resolve()

    return filepath


def write_file(location: Path|str, content):
    parent_dir=Path(location).parent

    if location.exists():
        raise Exception(f"file is already used {location}")

    if not parent_dir.exists():
        parent_dir.mkdir(exist_ok=True, parents=True)

    with open(location, "w") as f:
        f.write(content)


def normalize_args( *args: Path | str | list[Path|str]) -> list[Path]:
    normalized_args: list[Path]=[]

    for arg in args:
        if isinstance(arg, (str, Path)):
            normalized_args.append(Path(arg))

        # there could be a list given
        else:
            normalized_args.extend(Path(p) for p in arg)

    return normalized_args


def clean_folders( *paths: Path | str | list[Path|str] | set[Path|str]):
    normalize_paths: list[Path]=normalize_args(*paths)

    for folder in normalize_paths:
        if folder.exists() and folder.is_dir():
            shutil.rmtree(folder)


def get_all_yaml_files_in_dir_and_sub_dirs(folder: Path) -> list[Path]:
    all_yaml_files=[]

    files = folder.rglob("*.yaml")
    for f in files:
        all_yaml_files.append(f)

    return all_yaml_files


def read_yaml_from_string(yaml_string: str):
    yaml_dict:dict = yaml.safe_load(yaml_string)

    if not yaml_dict:
        raise Exception("problem reading from string")

    # There is always an outer_dict because of how the yaml is constructed, this is never needed, so pop this
    _, inner_dict = yaml_dict.popitem()

    return inner_dict

def read_yaml_from_filepath(filepath: Path):
    file_contents=read_file(filepath)
    yaml_dict=read_yaml_from_string(file_contents)

    if not yaml_dict:
        raise Exception("problem reading from path")

    return yaml_dict

def read_file(filepath: Path):
    file_contents=None

    with open(filepath, 'r') as file:
        file_contents = file.read()

    if file_contents is None:
        raise Exception("problem reading from path")

    return file_contents


def load_module(module_name, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)

    if spec is None or spec.loader is None:
        raise ImportError( f"Could not load module from {path}" )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module