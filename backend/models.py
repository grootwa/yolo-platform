from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ProjectModel(BaseModel):
    name: str = Field(..., example= " Hard Hat detection")
    description: Optional[str] = Field(None, example = "Industrial safety project")
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = Field(default="created") #created, training, completed

    class Config:
        json_schema_extra ={
            "example": {
                "name": "Industrial Project",
                "description": "Hard hat detection",
                "status": "created"
            }
        }