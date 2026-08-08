PROJECT_CONFIG_FILE_NAME = "project_config.yaml"
MODEL_CONFIG_FILE_NAME = "model_config.yaml"

# SPECIAL_KEY_WORDS
# These keywords that are available in the yaml are also used in the application
# So be carefull using these
PROJECT_CONFIG_MODELS_DIR_KEY = "models_dir"
PROJECT_CONFIG_TEMPLATES_DIR_KEY = "templates_dir"

MODEL_CONFIG_MODELS_KEYWORD = "models"
MODEL_CONFIG_OUTPUT_DIR_KEYWORD = "output_dir"
MODEL_CONFIG_GENERATION_CONFIG = "generation_config"

MODEL_CONFIG_ID_KEYWORD = "id"
MODEL_CONFIG_NAME_KEYWORD = "name"

GENERATION_CONFIG_TEMPLATE_KEY = "template"


# Application configs, we can also put this in project_config.yaml but i do not want people to
# adjust these
MAX_ITERATIONS_RESOLVER = 50