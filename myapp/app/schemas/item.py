from pydantic import BaseModel, Field
class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=500)
class ItemOut(BaseModel):
    id: int
    name: str
    description: str
    class Config:
        from_attributes = True