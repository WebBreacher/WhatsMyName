"""Site Schemas"""

from datetime import datetime
from typing import List, Optional, Dict, Any

from multidict import CIMultiDictProxy
from pydantic import BaseModel, root_validator


class SiteOutputSchema(BaseModel):
    """For exporting to csv, json"""
    raw_response_data: Optional[str] = None
    http_status_code: int
    generated_uri: str
    username: str
    user_agent: str
    uri_pretty: Optional[str] = None
    error_hint: Optional[str] = None
    response_headers: Optional[str] = None


class SiteSchema(BaseModel):
    name: str
    e_code: int
    e_string: str
    m_string: str
    m_code: int
    known: List[str]
    category: str
    valid: bool
    post_body: str
    uri_check: str
    request_method: str = None
    username: str = None
    generated_uri: str = None
    http_status_code: int = -1
    last_checked_on: Optional[datetime] = None
    comment: Optional[str] = None
    raw_response_data: Optional[str] = None
    cloudflare_enabled: bool = False
    user_agent: Optional[str] = None
    uri_pretty: Optional[str] = None
    error_hint: Optional[str] = None
    response_headers: Optional[str] = None
    invalid_chars: Optional[str]


    @root_validator
    def set_request_method(cls, values):
        if values.get('post_body'):
            values['request_method'] = 'POST'
        else:
            values['request_method'] = 'GET'
        return values

    class Config:
        fields = {'category': 'cat'}


class SitesConfigurationSchema(BaseModel):
    license: List[str] = []
    authors: List[str] = []
    categories: List[str] = []
    sites: List[SiteSchema] = []
