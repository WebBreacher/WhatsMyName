import json
from typing import List

from whatsmyname.app.models.schemas.sites import SiteSchema, SitesConfigurationSchema


def json_file_extractor(file_path: str) -> List[SiteSchema]:
    """
    Opens a json file, validates it and returns the Site instance
    :param file_path: str
    :return: List[Site]
    """
    with open(file_path) as json_file:
        json_data = json.load(json_file)
        sites_configuration = SitesConfigurationSchema(**json_data)
        return sites_configuration.sites

