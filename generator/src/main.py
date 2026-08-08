# Python libs
import json
from pathlib import Path
import shutil
from jinja2 import Environment
import yaml
import re
import ast

# Own libs
import constants
from jinja import create_jinja2_env
from resolver import ResolveContext, resolve
import singletons.application_arguments as application_arguments
import singletons.project_config as project_config


def main():
    # Get the location of the generator file and the parent dir
    project_config_abs_path:Path = get_abs_generator_config_path(application_arguments.get().project_config_path)

    # Initalize the singleton for generator file config
    setup_workplace_singleton(project_config_abs_path)

    # all model files
    all_model_config_file_paths_abs: list[Path] = get_all_models_config_files(project_config.get().project_config)

    # Get all template config, aka everything that has to be generated
    list_of_model_configs=get_model_configs(all_model_config_file_paths_abs)

    for model_config in list_of_model_configs:
        # print(template_config)
        print(json.dumps (model_config, indent=4, sort_keys=True))
        # generate all templates

    generate_templates(list_of_model_configs)

def generate_templates(list_of_model_configs):
    templates_dir=get_abs_path_of_file_and_validate(
        project_config.get().project_config[constants.PROJECT_CONFIG_TEMPLATES_DIR_KEY],
        project_config.get().project_abs_dir)
    jinja2_env = create_jinja2_env(templates_dir)

    clean_folders_to_be_used(list_of_model_configs)

    for model in list_of_model_configs:
        for generation_config in model[constants.MODEL_CONFIG_GENERATION_CONFIG]:
            if constants.GENERATION_CONFIG_TEMPLATE_KEY:
                generate_based_on_template(model, generation_config, jinja2_env)


def generate_based_on_template(model, generation_config, jinja2_env: Environment):
    # Get the output
    template = jinja2_env.get_template(generation_config[constants.GENERATION_CONFIG_TEMPLATE_KEY])
    output = template.render(model={})

    # The output dir 
    output_dir=Path(model[constants.MODEL_CONFIG_OUTPUT_DIR_KEYWORD])

    # Name of the to be written file
    file_name=""
    if constants.MODEL_CONFIG_NAME_KEYWORD in model:
        file_name=model[constants.MODEL_CONFIG_NAME_KEYWORD]
    elif constants.MODEL_CONFIG_ID_KEYWORD in model:
        file_name=model[constants.MODEL_CONFIG_ID_KEYWORD]
    else:
        raise Exception("There is no name or id in the model_config")

    # Get the suffix after templatename and before jinja2, so example.sql.jinja -> .sql
    file_extension=Path(template.name).with_suffix("").suffix

    # Full path for to be written file:
    file_path=Path(f"{output_dir}{file_name}{file_extension}")

    write_file(file_path , output)

def write_file(location: Path, content):
    parent_dir=location.parent

    if not parent_dir.exists():
        parent_dir.mkdir(exist_ok=True, parents=True)

    with open(location, "w") as f:
        f.write(content)


def clean_folders_to_be_used(list_of_model_configs: list[Path]):
    folders_to_be_cleaned=set()

    for model in list_of_model_configs:
        if not constants.MODEL_CONFIG_OUTPUT_DIR_KEYWORD in model:
            continue

        output_dir=Path(model[constants.MODEL_CONFIG_OUTPUT_DIR_KEYWORD])

        if not output_dir.exists() or not output_dir.is_dir():
            continue

        folders_to_be_cleaned.add(output_dir)

    for folder in folders_to_be_cleaned:
        shutil.rmtree(folder)
    

def get_model_configs(all_model_config_file_paths_abs: list[Path]):
    all_model_configs=[]

    for model_config_file_path_abs in all_model_config_file_paths_abs:
        model_config_root_folder= model_config_file_path_abs.parent
        all_yaml_config_paths_in_model=get_all_yaml_files_in_sub_dirs(model_config_root_folder)

        for yaml_file_path in all_yaml_config_paths_in_model:
            model_configs=create_squashed_template_configs(yaml_file_path, all_yaml_config_paths_in_model, model_config_file_path_abs)
            all_model_configs.extend(model_configs)

    for model in all_model_configs:
        validate_and_correct_model_config(model)

    return all_model_configs


def validate_and_correct_model_config(model: dict):
    # Check if output_dir is valid 
    # Also correct it to an abs path
    if constants.MODEL_CONFIG_OUTPUT_DIR_KEYWORD in model:
        output_dir=get_abs_path_of_file(model[constants.MODEL_CONFIG_OUTPUT_DIR_KEYWORD], project_config.get().project_abs_dir)

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


def get_all_yaml_files_in_sub_dirs(folder: Path) -> list[Path]:
    all_yaml_files=[]

    files = folder.rglob("*.yaml")
    for f in files:
        all_yaml_files.append(f)

    return all_yaml_files


def get_all_models_config_files(models_dir: Path | str) -> list[Path]:
    models_dir=get_abs_path_of_file_and_validate(
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


def setup_workplace_singleton(project_config_abs_path: Path):
    project_config.set_path(project_config_abs_path)
    # The working dir is the dir of the config file. Can change it so later an argument can be given to change this
    # This means all relative paths in projects, should be assuming this as working dir
    project_config.set_dir(project_config_abs_path.parent)

    # Set up config
    project_config_dict=read_yaml(project_config_abs_path)

    # resolve the project_config
    project_config_dict=resolve(project_config_dict, ResolveContext(project=project_config_dict))
    project_config.set_config(project_config_dict)

    print("Project_config: ", json.dumps (project_config_dict, indent=4, sort_keys=True))

    
def get_abs_generator_config_path(project_config_path_str: str):
    try:
        project_config_path: Path=get_abs_path_of_file_and_validate(project_config_path_str)

        if project_config_path.is_file():
            return project_config_path

        raise Exception
    except Exception as e:
        raise Exception(f"argument for project_config_path is not valid, {project_config_path_str} does not point to a valid file.")


def get_abs_path_of_file(filepath: str|Path, abs_base_dir:Path=None) -> Path:
    # Create copy of object, to not modify original object
    filepath = Path(filepath)

    if not filepath.is_absolute():
        if abs_base_dir:
            filepath=abs_base_dir.joinpath(filepath).resolve()
        else:
            filepath= filepath.resolve()

    return filepath

def get_abs_path_of_file_and_validate(filepath: str|Path, abs_base_dir:Path=None) -> Path:
    filepath = get_abs_path_of_file(filepath, abs_base_dir)

    if not filepath.exists():
        raise Exception(f"{filepath} file path does not exist")

    return filepath


def read_yaml(filepath):
    with open(filepath, 'r') as file:
        yaml_dict:dict = yaml.safe_load(file)

    if not yaml_dict:
        return None

    # There is always an outer_dict because of how the yaml is constructed, this is never needed, so pop this
    _, inner_dict = yaml_dict.popitem()

    return inner_dict


if __name__ == "__main__":
    main()