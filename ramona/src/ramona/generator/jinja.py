from pathlib import Path

from jinja2 import Environment, FileSystemLoader

def create_jinja2_env(tempalte_location: Path) -> Environment:
    env = Environment(
        loader=FileSystemLoader(tempalte_location),
        lstrip_blocks=True,
        trim_blocks=True
    )

    return env