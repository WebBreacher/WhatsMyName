""" Schema class for the user agent """
from pydantic import BaseModel


class UserAgentSchema(BaseModel):
    user_agent: str
    platform: str
