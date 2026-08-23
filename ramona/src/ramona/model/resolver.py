from functools import partial
import json
import re
from dataclasses import dataclass, field
from typing import Any

from jinja2.nativetypes import NativeEnvironment
from jinja2 import Environment

from ramona.model.classes.RamonaProject import Model, RamonaProject
from ramona.model.reference_resolver import TempRefClass
from ramona.utils.classes.DataclassEncoder import DataclassEncoder
from ramona.utils.file_handler import read_yaml_from_string
from ..utils import constants


class ResolveContext:
    def __init__(self, ramona_project=None, model=None, scope=None, _parents=[], _this=None):
        self.ramona_project = ramona_project   
        self.model = model
        self.scope = scope
        self._parents=_parents
        self._this = _this

# Ai, geen idee wat het doet
UNQUOTED_JINJA = re.compile( r"^(?P<prefix>\s*[^:]+:\s*)(?P<jinja>{{.*}})(?P<suffix>\s*)$")


# ============================================================
# Main resolver
# ============================================================

def resolve_jinja_yaml(string_to_resolve: str, resolve_context: ResolveContext) -> dict[str, Any]:
    """
    Resolve any object recursively.
    """
    # preprocess
    resolver = Jinja2YamlResolver(string_to_resolve, resolve_context)
    return resolver.resolve()

class Jinja2YamlResolver:
    def __init__(self, string_to_resolve: Any, resolve_context: ResolveContext):
        # Create class vars
        self.string_to_resolve=string_to_resolve
        self.starting_resolve_context=resolve_context

    # ============================================================
    # Resolvers
    # ============================================================
    def resolve(self):
        # Preprocess string
        self.prepocessed_string, self.placeholder_mapping=self._preprocess_yaml_with_jinja_string(self.string_to_resolve)
        self.object_to_resolve=read_yaml_from_string(self.prepocessed_string)

        # Prepare resolve_context
        self.starting_resolve_context._this=self.object_to_resolve
        return self._resolve(self.object_to_resolve, self.starting_resolve_context)


    def _resolve(self, object_to_resolve: Any, resolve_context: ResolveContext):
        if isinstance(object_to_resolve, dict):
            result: dict[str, Any] = {}

            for key, child in object_to_resolve.items():
                result[key] = self._resolve(
                    child, 
                    ResolveContext(
                        ramona_project=resolve_context.ramona_project,
                        model=resolve_context.model,
                        scope=resolve_context.scope,
                        _parents=list(resolve_context._parents) + [resolve_context._this],
                        _this=object_to_resolve
                    )
                )     
            return result

        if isinstance(object_to_resolve, list):
            return [self._resolve(item, 
                                  ResolveContext(
                                    ramona_project=resolve_context.ramona_project,
                                    model=resolve_context.model,
                                    scope=resolve_context.scope,
                                    _parents=list(resolve_context._parents),
                                    _this=object_to_resolve
                                )) for item in object_to_resolve]

        if object_to_resolve in self.placeholder_mapping:
            native_jinja2_env=self._load_jinja2_env(NativeEnvironment(), resolve_context)
            resolved_object = self._resolve_jinja_template(self.placeholder_mapping[object_to_resolve], native_jinja2_env)

            # If it is a string, it is resolved, and dont need to process it further
            # Except when i gives back a placeholder value, then we need to do one more loop
            if isinstance(resolved_object, str) and not resolved_object in self.placeholder_mapping:
                return resolved_object

            return self._resolve(resolved_object, resolve_context)

        if isinstance(object_to_resolve, str) :
            string_jinja2_env=self._load_jinja2_env(Environment(), resolve_context)
            resolved_string=self._resolve_jinja_template(object_to_resolve, string_jinja2_env)

            # Sometimes the placeholders bleed trough, and then we have to do an extra loop
            if resolved_string in self.placeholder_mapping:
                return self._resolve(resolved_string, resolve_context)

            return resolved_string
        else:
            return object_to_resolve

    def _resolve_jinja_template(self, value: str, environment: Environment | NativeEnvironment):
        rendered_string=""
        string_to_render=value
        i=0

        while i < constants.MAX_ITERATIONS_RESOLVER:
            i+=1

            rendered_string = environment.from_string(string_to_render).render()

            if string_to_render == rendered_string or not isinstance(rendered_string, str):
                break

            string_to_render = rendered_string

        return rendered_string

    # ============================================================
    # Helper functions
    # ============================================================
    def _load_jinja2_env(self, env : NativeEnvironment | Environment, resolve_context: ResolveContext) -> NativeEnvironment:
        env = env

        env.globals["project"] = partial(self.resolver_project, resolve_context=resolve_context)
        env.globals["this"] = partial(self.resolver_this, resolve_context=resolve_context)
        env.globals["model"] = partial(self.resolver_model, resolve_context=resolve_context)
        env.globals["scope"] = partial(self.resolver_scope, resolve_context=resolve_context)
        env.globals["ref"] = partial(self.resolver_ref, resolve_context=resolve_context)

        return env

    def _preprocess_yaml_with_jinja_string(self, string_to_resolve):
        placeholder_mapping={}
        final_results=[]

        for line in string_to_resolve.splitlines(keepends=True):
            result:str=line
            match=UNQUOTED_JINJA.match(line)

            if match:
                expression=match.group("jinja")
                placeholder=f"__RAMONA_JINJA_{len(placeholder_mapping)}__"

                placeholder_mapping[placeholder]=expression
                result= line.replace(expression, placeholder, 1)

            final_results.append(result)

        return (
            "".join(final_results),
            placeholder_mapping
        )
    
    # ============================================================
    # Expression resolver
    # ============================================================
    def resolver_project(self, key: str , resolve_context: ResolveContext) -> Any:
        return resolve_context.ramona_project.get_from_project_config(key)

    def resolver_model(self, key: str, resolve_context: ResolveContext ) -> Any:
        return resolve_context.model.get_from_model_config(key)  

    def resolver_this(self, key: str , resolve_context: ResolveContext) -> Any:
        if key not in resolve_context._this:
            raise Exception(f"Problem resolving this {key} in object {resolve_context._this}")

        resolved_object=resolve_context._this[key]

        # Sometimes the placeholders bleed trough, and then we have to do an extra loop
        if isinstance(resolved_object, str) and resolved_object in self.placeholder_mapping:
            resolved_object = self._resolve(resolved_object, resolve_context)
        # The order in which the resolved happen are random, therefore a resolved key, might not be fully resolved yet
        # Pass it trough the resolver one more to resolve it
        elif isinstance(resolved_object, dict):
            resolved_object = self._resolve(
                resolved_object, 
                resolve_context=ResolveContext(
                                        ramona_project=resolve_context.ramona_project,
                                        model=resolve_context.model,
                                        scope=resolve_context.scope,
                                        _parents=list(resolve_context._parents) + [resolve_context._this],
                                        _this=resolved_object
                                    )
            )

        return resolved_object 

    def resolver_scope(self, key: str , resolve_context: ResolveContext) -> Any:
        resolved_object={}

        # -1 because the last one is this dict. If this is the case, the user has to use this
        for parent in reversed(resolve_context._parents[:-1]):
            if key in parent:
                resolved_object = parent[key]
                
        # The order in which the resolved happen are random, therefore a resolved key, might not be fully resolved yet
        # Pass it trough the resolver one more to resolve it
        if isinstance(resolved_object, dict):
            resolved_object = self._resolve(
                resolved_object, 
                resolve_context=ResolveContext(
                                        ramona_project=resolve_context.ramona_project,
                                        model=resolve_context.model,
                                        scope=resolve_context.scope,
                                        _parents=list(resolve_context._parents) + [resolve_context._this],
                                        _this=resolved_object
                                    )
            )

        if not resolved_object:
            raise Exception(f"{key} not found in scope")

        return resolved_object

    def resolver_ref(self, *args: str, resolve_context: ResolveContext) -> Any:
        model=None
        object=None

        if len(args) == 1:
            model=resolve_context.model
            object=args[0]
            
        if len(args) == 2:
            model=resolve_context.ramona_project.get_model_from_key(args[0])
            object=args[1]

        if len(args) > 2:
            raise Exception("The ref argument is used with 1 or 2 arguments.")

        return TempRefClass(
            resolve_context.ramona_project.id if "id" in resolve_context.ramona_project.id else "",
            model.id,
            object
         )