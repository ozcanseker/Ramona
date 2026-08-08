from dataclasses import dataclass
import argparse
import constants

# Hidden variable for arguments
_arguments: ApplicationArguments | None = None


@dataclass(frozen=True)
class ApplicationArguments:
    project_config_path: str


def get() -> ApplicationArguments:
    global _arguments

    if _arguments is None:
        parser = argparse.ArgumentParser()

        parser.add_argument(
            "-pcp", 
            "--project-config-path",
            help="the filepath of the project config file, abs and rel are both supported.",
            default=f"./{constants.PROJECT_CONFIG_FILE_NAME}",
            dest="project_config_path"
        )

        args = parser.parse_args()

        _arguments = ApplicationArguments(
            project_config_path=args.project_config_path
        )

    return _arguments