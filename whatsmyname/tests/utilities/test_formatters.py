"""Test the formatting functionality """
import csv
import json
from argparse import ArgumentParser
from typing import List

from whatsmyname.app.cli.args import get_default_args, arg_parser
from whatsmyname.app.models.schemas.cli import CliOptionsSchema
from whatsmyname.app.models.schemas.sites import SiteSchema, SiteOutputSchema
from whatsmyname.app.tasks.process import get_sites_list
from whatsmyname.app.utilities.formatters import to_json, to_csv
from pydantic import parse_obj_as


def get_default_cli_options() -> CliOptionsSchema:
    args: ArgumentParser = get_default_args()
    return arg_parser(args.parse_args(['-u', 'yooper', '-d', '--verbose']))


def test_to_json() -> None:
    cli_options: CliOptionsSchema = get_default_cli_options()
    sites_list: List[SiteSchema] = get_sites_list(cli_options)
    site: SiteSchema = sites_list[0]
    site.http_status_code = 200
    site.generated_uri = 'test_url'
    to_json(cli_options, [site])

    with open(cli_options.output_file) as fp:
        sites: List[SiteSchema] = parse_obj_as(List[SiteOutputSchema], json.load(fp))
        loaded_site: SiteSchema = sites[0]
        assert loaded_site.http_status_code == 200
        assert loaded_site.generated_uri == 'test_url'


def test_to_csv() -> None:
    cli_options: CliOptionsSchema = get_default_cli_options()
    sites_list: List[SiteSchema] = get_sites_list(cli_options)
    site: SiteSchema = sites_list[0]
    site.http_status_code = 200
    site.generated_uri = 'test_url'
    site.raw_response_data = '<html>'
    to_csv(cli_options, [site])

    with open(cli_options.output_file) as csvfile:
        reader = csv.DictReader(csvfile)
        row = next(reader)
        assert row['http_status_code'] == '200'
        assert row['generated_uri'] == 'test_url'

