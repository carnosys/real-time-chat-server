from pydantic import BaseModel


class ORMBaseModel(BaseModel):
    class Config:
        from_attributes = True
