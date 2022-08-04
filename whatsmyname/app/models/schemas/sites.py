import datetime
from typing import List
from pydantic import BaseModel, root_validator


class SiteSchema(BaseModel):
    name: str
    e_code: int
    e_string: str
    m_string: str
    m_code: int
    known: List[str]
    cat: str
    valid: bool
    post_body: str
    uri_check: str
    request_method: str = None
    username: str = None
    generated_uri: str = None
    http_status_code: int = -1


    @root_validator
    def set_request_method(cls, values):
        if values.get('post_body'):
            values['request_method'] = 'POST'
        else:
            values['request_method'] = 'GET'
        return values


class SitesConfigurationSchema(BaseModel):
    license: List[str] = []
    authors: List[str] = []
    categories: List[str] = []
    sites: List[SiteSchema] = []





