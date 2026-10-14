# schemas.py - Base Pydantic Validation Schemas
from pydantic import BaseModel, ConfigDict
from typing import Optional, Any

class BaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    status: str = "success"
    message: Optional[str] = None
    data: Optional[Any] = None
