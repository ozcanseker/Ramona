class Commands:
    GENERATE = "generate"
    MODELCHECK = "modelcheck"

commands = Commands()


# SPECIAL_KEY_WORDS
# These keywords that are available in the yaml are also used in the application
# So be carefull using these
class ProjectConfigKeys:
    MODELS_DIR_KEY = "models_dir"
    TEMPLATES_DIR_KEY = "templates_dir"
    ALWAYS_CLEAN_KEY = "always_clean"
    MODELCHECKS_KEY = "modelchecks_dir"

project_config_keys = ProjectConfigKeys()


class FileLoader:
    MODULE_PREFIX = "ramona_modelcheck_"

fileloader = FileLoader()


class ModelKeys:
    MODELS = "models"
    OUTPUT_DIR = "output_dir"
    GENERATION_CONFIG = "generation_config"

    MODEL_ID = "id"
    MODEL_NAME = "name"
    MODEL_FILENAME = "file_name"

    
    ABS_FILE_PATH = "absolute_file_path"

model_keys = ModelKeys()


class FileNames:
    PROJECT_CONFIG = "project_config.yaml"
    MODEL_CONFIG = "model_config.yaml"

filenames = FileNames()





GENERATION_CONFIG_TEMPLATE_KEY = "template"


# Application configs, we can also put this in project_config.yaml but i do not want people to
# adjust these
MAX_ITERATIONS_RESOLVER = 50