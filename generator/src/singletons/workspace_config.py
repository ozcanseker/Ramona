from dataclasses import dataclass
from pathlib import Path

@dataclass()
class WorkspaceConfig:
    workspace_config_abs_path: Path | None = None
    workspace_abs_dir: Path | None = None
    workspace_config: dict | None = None

_workspace_config: WorkspaceConfig = None

def set_path(workspace_config_path: Path):
    global _workspace_config

    if not _workspace_config:
        _workspace_config = WorkspaceConfig()
    
    if _workspace_config.workspace_config_abs_path:
        raise Exception("workspace_config_path already set")

    _workspace_config.workspace_config_abs_path = workspace_config_path

def set_dir(workspace_dir: Path):
    global _workspace_config

    if not _workspace_config:
        _workspace_config = WorkspaceConfig()
    
    if _workspace_config.workspace_abs_dir:
        raise Exception("workspace_config already set")

    _workspace_config.workspace_abs_dir = workspace_dir

def set_config(workspace_config: dict):
    global _workspace_config

    if not _workspace_config:
        _workspace_config = WorkspaceConfig()
    
    if _workspace_config.workspace_config:
        raise Exception("workspace_config already set")

    _workspace_config.workspace_config = workspace_config


def get() -> WorkspaceConfig:
    global _workspace_config

    if not _workspace_config:
        raise Exception("workspace_config not set")

    return _workspace_config
