class Commands:
    GENERATE = "generate"
    MODELCHECK = "modelcheck"

commands = Commands()


class FileNames:
    RAMONA_CONFIG = "ramona.yaml"
    MODEL_CONFIG_NAMES = ["model_config.yaml", "model_config.yml"]
    MODEL_CONFIG_EXTENSIONS = ["*.yaml", "*.yml"]

filenames = FileNames()


class FileLoader:
    MODULE_PREFIX = "ramona_modelcheck_"

fileloader = FileLoader()


# SPECIAL_KEY_WORDS
# These keywords that are available in the yaml are also used in the application
# So be carefull using these

class GenericKeys:
    ID = "id"
    NAME = "name"
    OUTPUT_DIR = "output_dir"

generic_keys = GenericKeys()


class ProjectConfigKeys(GenericKeys):
    MODELS_DIR = "models_dir"
    TEMPLATES_DIR = "templates_dir"
    GENERATED_PATHS = "generated_paths"
    MODELCHECKS = "modelchecks_dir"

project_config_keys = ProjectConfigKeys()

class ModelKeys(GenericKeys):
    OBJECTS = "objects"

model_keys = ModelKeys()


class ObjectKeys(GenericKeys):
    CHILD_OBJECTS = "child_objects"
    TEMPLATE_CONFIG = "template_config"
    FILENAME = "file_name"

object_keys = ObjectKeys()


class TemplateKeys(GenericKeys):
    TEMPLATE = "template"
    COPY_FROM = "copy_from"

template_keys = TemplateKeys()


# Application configs, we can also put this in project_config.yaml but i do not want people to
# adjust these
MAX_ITERATIONS_RESOLVER = 50
LOG_LOCATION="./log/ramona.log"
LOGGER_NAME="ramona"