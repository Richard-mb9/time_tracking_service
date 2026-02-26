import importlib
from pathlib import Path


def import_mappers() -> None:
    current_dir = Path(__file__).parent

    for file_path in current_dir.glob("*.py"):
        if file_path.name not in ("__init__.py", "mapper_config.py"):
            module_name = f"infra.mappers.{file_path.stem}"
            importlib.import_module(module_name)
