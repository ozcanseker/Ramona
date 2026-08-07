from dataclasses import dataclass
import argparse
import constants

# Hidden variable for arguments
_arguments: ApplicationArguments | None = None


@dataclass(frozen=True)
class ApplicationArguments:
    workspace_config_path: str


def get() -> ApplicationArguments:
    global _arguments

    if _arguments is None:
        parser = argparse.ArgumentParser()

        parser.add_argument(
            "-wcp", 
            "--workspace-config-path",
            help="the filepath of the workspace config file, abs and rel are both supported.",
            default=f"./{constants.WORKSPACE_CONFIG_FILE_NAME}",
            dest="workspace_config_path"
        )

        args = parser.parse_args()

        _arguments = ApplicationArguments(
            workspace_config_path=args.workspace_config_path
        )

    return _arguments