import json
from pathlib import Path

from ramona.model.resolver import ResolveContext, resolve
from ramona.singletons import project_config
from ramona.utils import constants
from ramona.utils.file_handler import get_abs_path, get_abs_path_and_validate_if_exists, get_all_yaml_files_in_dir_and_sub_dirs, read_yaml


def get_model_configs():
    all_model_config_file_paths_abs=get_all_models_config_files(project_config.get().project_config)
    all_model_configs=[]

    for model_config_file_path_abs in all_model_config_file_paths_abs:
        model_config_root_folder= model_config_file_path_abs.parent
        all_yaml_config_paths_in_model=get_all_yaml_files_in_dir_and_sub_dirs(model_config_root_folder)

        for yaml_file_path in all_yaml_config_paths_in_model:
            model_configs=create_squashed_template_configs(yaml_file_path, all_yaml_config_paths_in_model, model_config_file_path_abs)
            all_model_configs.extend(model_configs)

    for model in all_model_configs:
        validate_and_correct_model_config(model)

    return all_model_configs


def get_all_models_config_files(models_dir: Path | str) -> list[Path]:
    models_dir=get_abs_path_and_validate_if_exists(
        models_dir[constants.PROJECT_CONFIG_MODELS_DIR_KEY], 
        project_config.get().project_abs_dir
        )
    
    all_model_dirs:list[Path]=[]

    files = models_dir.rglob(constants.MODEL_CONFIG_FILE_NAME)
    for f in files:
        all_model_dirs.append(f)

    # Also validate that there are not model_config.yaml inside another model_config.yaml
    for f in all_model_dirs:
        for f2 in all_model_dirs:
            if f is not f2 and f.parent in f2.parents:
                raise Exception("every model should have only one model_config")

    return all_model_dirs


def validate_and_correct_model_config(model: dict):
    # Check if output_dir is valid 
    # Also correct it to an abs path
    if constants.MODEL_CONFIG_OUTPUT_DIR_KEYWORD in model:
        output_dir=get_abs_path(model[constants.MODEL_CONFIG_OUTPUT_DIR_KEYWORD], project_config.get().project_abs_dir)

        if not project_config.get().project_abs_dir in output_dir.parents:
            print(json.dumps(model, indent=4, sort_keys=True))
            raise Exception("Output dir is set to something outside the project path",
                            f"output_dir={output_dir}"
            )

        # Set the output dir as an abs path
        model[constants.MODEL_CONFIG_OUTPUT_DIR_KEYWORD]=str(output_dir)


def create_squashed_template_configs(yaml_file_path, all_yaml_configs_paths_in_model, model_config_file_path_abs):
    parent_yaml_files_sorted = parent_yaml_files_sorted_highest_first(yaml_file_path, all_yaml_configs_paths_in_model, model_config_file_path_abs)
    yaml_config = read_yaml(yaml_file_path)
    model_config_config=read_yaml(model_config_file_path_abs)
    all_model_configs=[]
    
    if not yaml_config or constants.MODEL_CONFIG_MODELS_KEYWORD not in yaml_config:
        return []

    for model in yaml_config[constants.MODEL_CONFIG_MODELS_KEYWORD]:
        final_config = dict(project_config.get().project_config)

        for parent_yaml_file_path in parent_yaml_files_sorted:
            parent_yaml_config=read_yaml(parent_yaml_file_path)
            final_config=squash_dicts(final_config, parent_yaml_config, model_config_config)

        # Fully squashed dict
        final_config = squash_dicts(final_config, model, model_config_config)
        all_model_configs.append(final_config)

    return all_model_configs


def squash_dicts(parent_dict, leading_dict, model_config_config):
    leading_dict = resolve(
        dict(leading_dict),
        ResolveContext(
            project=project_config.get().project_config,
            parent_yaml=parent_dict,
            model=model_config_config
        )
    )

    return (parent_dict | leading_dict)


def parent_yaml_files_sorted_highest_first(yaml_file_path: Path, all_yaml_configs_paths_in_model: list[Path], model_config_file_path_abs: Path):
    if yaml_file_path == model_config_file_path_abs:
        return []

    # First remove all child yaml paths
    parent_yaml_files=[ parent for parent in all_yaml_configs_paths_in_model if parent.parent in yaml_file_path.parents ]

    parent_yaml_files.remove(model_config_file_path_abs)

    # Also remove same level yaml paths because those are not parent
    parent_yaml_files=[ path for path in parent_yaml_files if yaml_file_path.parent != path.parent ]

    parent_yaml_files.sort(
        key = lambda item : (len(item.parents), item.name)
    )

    return_list = [model_config_file_path_abs]
    return_list.extend(parent_yaml_files)

    return return_list
