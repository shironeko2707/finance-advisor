from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class MissingField(BaseModel):
    """
    Represents a field identified as missing by the LLM.
    """
    field_name: str = Field(..., description="Name of the missing field")
    # description: str = Field(..., description="Description of what this field represents")
    # row_index: int = Field(..., description="Row index in the table where this field is located")
    # column_indices: List[int] = Field(..., description="Column indices that need to be filled")


class MissingFieldsAnalysis(BaseModel):
    """
    Complete analysis of missing fields in the table.
    """
    missing_fields: List[MissingField] = Field(..., description="List of all identified missing fields")
    # total_missing_count: int = Field(..., description="Total number of missing fields found")
    # analysis_summary: str = Field(..., description="Summary of the missing fields analysis")


class SearchCandidate(BaseModel):
    """
    Represents a single candidate result from a data search.

    Attributes:
        value (str): The matched value or content found during the search.
        file_name (str): The name of the file where the candidate was found.
        page (int): The page number (or sheet/section) within the file where the candidate appears.
        score (Optional[float]): The confidence score for this candidate (optional).
    """
    value: str = Field(..., description="The matched value or content found during the search.")
    file_name: str = Field(..., description="The name of the file where the candidate was found.")
    page: int = Field(..., description="The page number (or sheet/section) within the file where the candidate appears.")
    score: Optional[float] = Field(None, description="The confidence score for this candidate (optional).")


class SearchResult(BaseModel):
    """
    Represents the result of a data search, including all candidates and the final selected result.

    Attributes:
        candidates (List[SearchCandidate]): A list of all candidate results found during the search.
        final_result (SearchCandidate): The candidate selected as the final result.
        reason (str): The rationale or explanation for selecting the final result.
    """
    candidates: List[SearchCandidate] = Field(..., description="A list of all candidate results found during the search.")
    final_result: SearchCandidate = Field(..., description="The candidate selected as the final result.")
    reason: str = Field(..., description="The rationale or explanation for selecting the final result.")

    @property
    def calculate_confidence(self) -> Optional[float]:
        pass


class FillInValue(BaseModel):
    """
    Represents a filled-in value for a specific cell in a table.

    Attributes:
        result (SearchResult): The search result for this cell, including all candidates and the selected value.
        row_field (str): Name of the row of the missing cell.
        col_field (str): Name of the column of the missing cell.
    """
    result: SearchResult = Field(..., description="The search result for this cell, including all candidates and the selected value.")
    row_field: str = Field(..., description="Name of the row of the missing cell, for example `Interest income`.")
    col_field: str = Field(..., description="Name of the column of the missing cell, for example `2016`.")


class FillInValues(BaseModel):
    """
    Represents a collection of filled-in values for a table.

    Attributes:
        values (List[FillInValue]): List of filled-in values for the table.
    """
    values: List[FillInValue] = Field(..., description="List of filled-in values for the table.")
