from ninja import Schema, Field
from typing import List

class CopySchema(Schema):
    pid: int = Field(alias='project_id')
    data: List[str] = Field(alias='checkedNodes')
