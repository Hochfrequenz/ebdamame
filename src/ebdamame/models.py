"""
Model classes for ebdamame.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EbdNoTableSection(BaseModel):
    """
    Represents an empty section in the document.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    ebd_key: str
    remark: str


class EbdChapterInformation(BaseModel):
    """
    Contains information about where an EBD is located within the document.
    If the heading is e.g. "5.2.1" we denote this as:
    * chapter 5
    * section 2
    * subsection 1
    """

    model_config = ConfigDict(frozen=True)

    chapter: int = Field(ge=1)
    chapter_title: Optional[str] = None
    section: int = Field(ge=1)
    section_title: Optional[str] = None
    subsection: int = Field(ge=1)
    subsection_title: Optional[str] = None
