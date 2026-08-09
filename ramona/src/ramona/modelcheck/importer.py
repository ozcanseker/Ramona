from pathlib import Path
import importlib.util


def load_checks(directory: Path):

    for file in directory.rglob("*.py"):

        if file.name == "__init__.py":
            continue

        module_name = f"_modelcheck_{file.stem}"

        spec = importlib.util.spec_from_file_location(
            module_name,
            file,
        )

        if spec is None or spec.loader is None:
            raise ImportError(
                f"Could not load check module: {file}"
            )

        module = importlib.util.module_from_spec(spec)

        spec.loader.exec_module(module)