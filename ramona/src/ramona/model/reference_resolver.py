from dataclasses import dataclass
import logging
from typing import Any

from ramona.model.classes.RamonaProject import Object, RamonaProject
from ramona.utils import constants

logger=logging.getLogger(__name__)


@dataclass(frozen=True)
class TempRefClass:
    project: str
    model: str
    object: str


def resolve_references(ramona_project: RamonaProject):
    all_objects=ramona_project.get_all_objects_as_list()

    for object in all_objects:
        object.object_config=_resolver_references(object.object_config, ramona_project)
     
def _resolver_references(object_to_resolve, ramona_project: RamonaProject):
    if isinstance(object_to_resolve, dict):
        result: dict[str, Any] = {}

        for key, child in object_to_resolve.items():
            result[key] = _resolver_references(child, ramona_project)     

        return result

    if isinstance(object_to_resolve, list): 
        return [_resolver_references(item, ramona_project) for item in object_to_resolve]

    return _resolve_ref(object_to_resolve, ramona_project)

def _resolve_ref(object_to_resolve, ramona_project: RamonaProject):
    # print(type(object_to_resolve))
    # print(object_to_resolve)
    if not isinstance(object_to_resolve, TempRefClass):
        return object_to_resolve

    object_to_resolve: TempRefClass = object_to_resolve
    model=ramona_project.get_model_from_key(object_to_resolve.model)
    object=model.get_object_from_key(object_to_resolve.object)
    return object