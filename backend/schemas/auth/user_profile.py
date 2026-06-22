
from pydantic import BaseModel, ConfigDict

class UserProfile(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    email: str

    model_config = ConfigDict(from_attributes=True)
