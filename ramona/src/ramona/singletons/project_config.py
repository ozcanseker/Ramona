from dataclasses import dataclass
from pathlib import Path

@dataclass()
class ProjectConfig:
    project_config_abs_path: Path | None = None
    project_abs_dir: Path | None = None
    project_config: dict | None = None

_project_config: ProjectConfig = None

def set_path(project_config_path: Path):
    global _project_config

    if not _project_config:
        _project_config = ProjectConfig()
    
    if _project_config.project_config_abs_path:
        raise Exception("project_config_path already set")

    _project_config.project_config_abs_path = project_config_path

def set_dir(project_dir: Path):
    global _project_config

    if not _project_config:
        _project_config = ProjectConfig()
    
    if _project_config.project_abs_dir:
        raise Exception("project_config already set")

    _project_config.project_abs_dir = project_dir

def set_config(project_config: dict):
    global _project_config

    if not _project_config:
        _project_config = ProjectConfig()
    
    if _project_config.project_config:
        raise Exception("project_config already set")

    _project_config.project_config = project_config


def get() -> ProjectConfig:
    global _project_config

    if not _project_config:
        raise Exception("project_config not set")

    return _project_config

def get_key(key) -> ProjectConfig:
    global _project_config

    if not _project_config or not _project_config.project_config:
        raise Exception("project_config not set")

    return _project_config.project_config[key]
