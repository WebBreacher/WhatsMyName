""" Holds the schema for all the command line options """

from typing import Optional, List
from pydantic import BaseModel, Field
from whatsmyname.app.models.enums.common import OutputFormat


class CliOptionsSchema(BaseModel):
    all: bool = False
    input_file: Optional[str] = None
    debug: bool = False
    output: bool = False
    sites: Optional[List[str]] = []
    category: Optional[str] = None
    string_error: bool = False
    usernames: Optional[List[str]] = []
    follow_redirects: bool = False
    timeout: int = 30
    format: OutputFormat = OutputFormat.JSON
    output_file: Optional[str] = None
    output_stdout: bool = False
    per_request_timeout: int = 5
    not_found: bool = False
    verbose: bool = False
    max_redirects: int = 10
    random_validate: bool = False
    random_username: Optional[str] = None,
    user_agent_id: int = 1
    user_agent: Optional[str] = None
    capture_errors: bool = False
    capture_error_directory: Optional[str] = None
    validate_knowns: bool = False
    add_error_hints: bool = False
    word_wrap_length: int = 50




