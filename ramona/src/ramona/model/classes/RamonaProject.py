import json
from pathlib import Path


class RamonaProject:
    project_config_file_path: Path=None
    project_folder: Path=None
    project_config: dict[str, str]=None
    models : dict[str, Model] =None

    def __init__(self, project_config_file_path: Path):
        self.project_config_file_path=project_config_file_path
        self.project_folder=project_config_file_path.parent

        self.models={}

    @property
    def id(self):
        return self.project_config['id']

    def set_project_config(self, project_config: dict[str, str]):
        self.project_config = project_config    

    def get_from_project_config(self, key: str):
        return self.project_config[key]

    def register_model(self, model: Model) -> Model:
        if "id" not in model.model_config:
            raise Exception(f"Model {model.model_config_file_path} has no id.")

        if model.id in self.models:
            raise Exception(f"Models with duplicate ids: {model.id}")

        self.models[model.id]=model

    def get_models_as_list(self):
        return list(self.models.values())
        
    def __repr__(self):
        return "\n".join([
            "RamonaProject:",
            f"config_path={self.project_config_file_path}",
            f"project_folder={self.project_folder}",
            f"project_config=",
            json.dumps(self.project_config, indent=4, sort_keys=True)
        ])


class Model:
    model_config_file_path: str = None
    model_folder: str = None
    model_config: dict[str, str]=None
    all_yaml_config_paths_in_model: list[Path]=None
    objects: dict[str, Object] =None

    def __init__(self, model_config_file_path: Path):
        self.model_config_file_path=model_config_file_path
        self.model_folder=model_config_file_path.parent

        self.objects={}

    @property
    def id(self):
        return self.model_config['id']

    def __repr__(self):
        return "\n".join([
            "Model:",
            f"model_config_file_path={self.model_config_file_path}",
            f"model_folder={self.model_folder}",
            f"model_config=",
            json.dumps(self.model_config, indent=4, sort_keys=True)
        ])

    def get_from_model_config(self, key):
        return self.model_config[key]


class Object:
    object_id: str
    object_config: dict