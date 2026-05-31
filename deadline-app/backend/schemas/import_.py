from pydantic import BaseModel, ConfigDict


class DetectTabsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sheet_names: list[str]
    suggested: dict


class ParseRequest(BaseModel):
    tab1_name: str
    tab2_name: str


class ImportSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    documents_parsed: int
    directives_parsed: int
    total_flagged: int
    staff_found: int
