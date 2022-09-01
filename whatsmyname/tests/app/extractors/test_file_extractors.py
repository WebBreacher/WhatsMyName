"""Test loading json files into objects
"""
import os
from argparse import ArgumentParser

from commonmark.blocks import List

from whatsmyname.app.cli.args import get_default_args, arg_parser
from whatsmyname.app.config import resource_dir
from whatsmyname.app.extractors.file_extractors import site_file_extractor, user_agent_extractor
from whatsmyname.app.models.schemas.cli import CliOptionsSchema
from whatsmyname.app.models.schemas.sites import SiteSchema
from whatsmyname.app.models.schemas.user_agent import UserAgentSchema


def test_site_file_extractor():
    args: ArgumentParser = get_default_args()
    schema: CliOptionsSchema = arg_parser(args.parse_args(['-u', 'yooper']))
    sites: List[SiteSchema] = site_file_extractor(schema.input_file)
    assert len(sites) > 0


def test_user_agent_extractor():
    user_agents: List[UserAgentSchema] = user_agent_extractor(os.path.join(resource_dir, 'user-agents.json'))
    assert len(user_agents) > 0