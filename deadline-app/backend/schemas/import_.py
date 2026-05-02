from pydantic import BaseModel
from typing import Optional

class DetectTabsResponse(BaseModel):
    sheet_names: list[str]
    suggested: dict 

class ParseRequest(BaseModel):
    tab1_name: str
    tab2_name: str 

class ImportSummary(BaseModel):
    documents_parsed: int
    directives_parsed: int
    total_flagged: int 
    staff_found: int 