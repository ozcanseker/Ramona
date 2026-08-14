class Commands:
    GENERATE = "generate"
    MODELCHECK = "modelcheck"

commands = Commands()


class FileNames:
    RAMONA_CONFIG = "ramona.yaml"
    MODEL_CONFIG = "model_config.yaml"

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

generic_keys = GenericKeys()


class ProjectConfigKeys(GenericKeys):
    MODELS_DIR = "models_dir"
    TEMPLATES_DIR = "templates_dir"
    ALWAYS_CLEAN = "always_clean"
    MODELCHECKS = "modelchecks_dir"

project_config_keys = ProjectConfigKeys()

class ModelKeys(GenericKeys):
    OBJECTS = "objects"

model_keys = ModelKeys()


class ObjectKeys(GenericKeys):
    CHILD_OBJECTS = "child_objects"
    GENERATION_CONFIG = "generation_config"
    OUTPUT_DIR = "output_dir"
    FILENAME = "file_name"

object_keys = ObjectKeys()


class GenerationKeys(GenericKeys):
    TEMPLATE = "template"
    COPY_TO_LOCATION = "copy_to_location"

generation_keys = GenerationKeys()


# Application configs, we can also put this in project_config.yaml but i do not want people to
# adjust these
MAX_ITERATIONS_RESOLVER = 50
LOG_LOCATION="./log/ramona.log"
LOGGER_NAME="ramona"