import argparse
from textwrap import dedent
from ramona.utils import constants


class ApplicationArguments:
    ramona_config_path: str
    command: str

    def __init__(self):
        pass

    def get_application_arguments(self) -> ApplicationArguments:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-rcp", 
            "--ramona-config-path",
            help="the filepath of the ramona config file, abs and rel are both supported.",
            default=f"./{constants.filenames.RAMONA_CONFIG}",
            dest="ramona_config_path"
        )

        subparsers = parser.add_subparsers(
            title="commands",
            dest="command",
            required=True,
        )

        generate_parser = subparsers.add_parser(
            constants.commands.GENERATE,
            help="Generate output from YAML models",
        ) 

        check_parser = subparsers.add_parser(
            constants.commands.MODELCHECK,
            help="Run model checks",
        )

        args = parser.parse_args()
        self.ramona_config_path=args.ramona_config_path
        self.command=args.command

        return self

    
    def __repr__(self):
        return "\n".join(["ApplicationArguments:",
                f"ramona_config_path={self.ramona_config_path}",
                f"command={self.command}"
        ])