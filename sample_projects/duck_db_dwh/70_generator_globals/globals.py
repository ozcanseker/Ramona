

from pathlib import Path
import re
import hashlib

from ramona.generator.decorator import generator_global_function
from ramona.model.classes.RamonaProject import RamonaProject


@generator_global_function
def to_relative_path(context, file_path):
    proj: RamonaProject = context["project"]

    return str(Path(file_path).relative_to(proj.project_folder).as_posix())


_SQL_LINE_COMMENT = re.compile(r"--[^\r\n]*")
_SQL_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
_SQL_WHITESPACE = re.compile(r"\s+")

@generator_global_function
def sql_file_hash(context, file_path: str) -> str:
    path = Path(file_path)

    sql = path.read_text(encoding="utf-8")

    # Remove SQL comments
    sql = _SQL_BLOCK_COMMENT.sub("", sql)
    sql = _SQL_LINE_COMMENT.sub("", sql)

    # Normalize whitespace
    sql = _SQL_WHITESPACE.sub(" ", sql).strip()

    return hashlib.sha256(sql.encode("utf-8")).hexdigest()[:16]