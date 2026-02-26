# pyright: reportUnusedImport=false
from sqlalchemy import MetaData
from sqlalchemy.orm import registry

from .mapper_config import import_mappers

metadata = MetaData()
mapper_registry = registry(metadata=metadata)
