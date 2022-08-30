import json
from typing import List

from pydantic import parse_obj_as

from whatsmyname.app.models.schemas.sites import SiteSchema, SitesConfigurationSchema
from whatsmyname.app.models.schemas.user_agent import UserAgentSchema


def site_file_extractor(file_path: str) -> List[SiteSchema]:
    """
    Opens a json file, validates it and returns the Site instance
    :param file_path: str
    :return: List[Site]
    """
    with open(file_path) as json_file:
        json_data = json.load(json_file)
        sites_configuration = SitesConfigurationSchema(**json_data)
        return sites_configuration.sites


def user_agent_extractor(file_path: str) -> List[UserAgentSchema]:
    """
    Opens a json file, validates it and returns a set of user agent instances
    :param file_path: str
    :return: List[UserAgent]
    """
    with open(file_path) as json_file:
        json_data = json.load(json_file)
        return parse_obj_as(List[UserAgentSchema], json_data)
