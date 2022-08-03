from typing import Optional, List

from pydantic import BaseModel

from whatsmyname.app.models.enums.common import OutputFormat


class CliOptionsSchema(BaseModel):
    input_file: Optional[str] = None
    debug: bool = False
    output: bool = False
    sites: Optional[List[str]] = []
    category: Optional[str] = None
    string_error: bool = False
    usernames: List[str] = []
    follow_redirects: bool = True
    timeout: Optional[int] = 30
    format: OutputFormat = OutputFormat.JSON
    output_file: Optional[str] = None
    output_stdout: bool = True


