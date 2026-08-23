from dataclasses import asdict, is_dataclass
import json
from pathlib import Path

from ramona.utils import constants
from ramona.utils.classes.DataclassEncoder import DataclassEncoder


class RamonaProject:
    project_config_file_path: Path=None
    project_folder: Path=None
    project_config: dict[str, str]=None
    models: dict[str, Model] =None
    objects: dict[str, Object] =None

    def __init__(self, project_config_file_path: Path):
        self.project_config_file_path=project_config_file_path
        self.project_folder=project_config_file_path.parent

        self.models={}
        self.objects={}

    def __getitem__(self, key):
        return self.project_config[key]

    def __contains__(self, key):
        return key in self.project_config

    def __setitem__(self, key, value):
        self.project_config[key]=value

    def __repr__(self):
        return "\n".join([
            "RamonaProject:",
            f"config_path={self.project_config_file_path}",
            f"project_folder={self.project_folder}",
            f"project_config=",
            json.dumps(self.project_config, indent=4, sort_keys=True, cls=DataclassEncoder),
        ])

    @property
    def id(self):
        return self.project_config['id']

    def set_project_config(self, project_config: dict[str, str]):
        self.project_config = project_config    

    def get_from_project_config(self, key: str):
        return self.project_config[key]

    def register_model(self, model: Model):
        if constants.model_keys.ID not in model.model_config:
            raise Exception(f"Model {model.model_config_file_path} has no id.")

        if getattr(model, constants.model_keys.ID) in self.models:
            raise Exception(f"Models with duplicate ids: {model.id}")

        self.models[model.id]=model

    def get_model_from_key(self, key: str):
        if key not in self.models:
            raise Exception("No model in project with key " + key)

        return self.models[key]

    def register_object(self, object: Object):
        if "id" not in object.object_config:
            raise Exception(f"Object {object.object_config_file_path} has no id.")

        if object.id in self.objects:
            raise Exception(f"Object with duplicate ids: {object.id}")

        self.objects[object.id]=object

    def get_models_as_list(self):
        return list(self.models.values())

    def get_all_model_objects_as_list(self):
        return [object for model in self.models.values() for object in model.objects.values()]

    def get_all_objects_as_list(self):
            return self.get_all_model_objects_as_list() + list(self.objects.values())


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

    def __getitem__(self, key):
        return self.model_config[key]

    def __contains__(self, key):
        return key in self.model_config

    def __setitem__(self, key, value):
        self.model_config[key]=value

    def __repr__(self):
        return "\n".join([
            "Model:",
            f"model_config_file_path={self.model_config_file_path}",
            f"model_folder={self.model_folder}",
            f"model_config=",
            json.dumps(self.model_config, indent=4, sort_keys=True, cls=DataclassEncoder)
        ])


    @property
    def id(self):
        return self.model_config['id']

    def register_object(self, object: Object):
        if "id" not in object.object_config:
            raise Exception(f"Model {object.object_config_file_path} has no id.")

        if object.id in self.objects:
            raise Exception(f"Models with duplicate ids:\n"
                            f"id: {object.id}\n"
                            f"file_path:{object.object_config_file_path}\n"
                            f"file_path_duplicate:{self.objects[object.id].object_config_file_path}\n"
                        )       

        self.objects[object.id]=object

    def get_object_from_key(self, key: str):
        if key not in self.objects:
            raise Exception("No object in model with key " + key)

        return self.objects[key]

    def get_from_model_config(self, key):
        return self.model_config[key]

    def get_config(self):
        return self.model_config

    def get_all_objects_as_list(self):
        return [object for object in self.objects.values()]

    def get_objects_for_path(self, yaml_file_path):
        all_obj = []

        for obj in self.objects.values():
            if obj.object_config_file_path == yaml_file_path:
                all_obj.append(obj)

        return all_obj


class Object:
    object_config_file_path: str
    object_config: dict

    def __init__(self, object_config_file_path, object_config):
        self.object_config_file_path = object_config_file_path
        self.object_config=object_config

    def __getitem__(self, key):
        return self.object_config[key]

    def __contains__(self, key):
        return key in self.object_config

    def __setitem__(self, key, value):
        self.object_config[key]=value
        pass

    def __repr__(self):
        return "\n".join([
            "Object:",
            f"object_config_file_path={self.object_config_file_path}",
            f"object_config=",
            json.dumps(self.object_config, indent=4, sort_keys=True, cls=DataclassEncoder)
        ])

    def __or__(self, other):
        return Object(
            self.object_config_file_path,
            self.object_config | other
        )

    def clone(self):
        return Object(
            self.object_config_file_path,
            dict(self.object_config)
        )

    @property
    def id(self):
        return self.object_config['id']

    def get_config(self):
        return self.object_config
