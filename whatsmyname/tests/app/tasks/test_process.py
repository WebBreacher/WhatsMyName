""" Test the functionality within the process module """
from argparse import ArgumentParser
from typing import List

from whatsmyname.app.cli.args import arg_parser, get_default_args
from whatsmyname.app.models.schemas.cli import CliOptionsSchema
from whatsmyname.app.models.schemas.sites import SiteSchema
from whatsmyname.app.tasks.process import get_sites_list, generate_username_sites, filter_list_by


def get_default_cli_options() -> CliOptionsSchema:
    args: ArgumentParser = get_default_args()
    return arg_parser(args.parse_args(['-u', 'yooper', '-d', '--verbose']))


def test_get_default_sites_list() -> None:
    cli_options: CliOptionsSchema = get_default_cli_options()
    sites_list: List[SiteSchema] = get_sites_list(cli_options)
    assert len(sites_list) > 100


def test_filtered_sites_list() -> None:
    cli_options: CliOptionsSchema = get_default_cli_options()
    cli_options.sites = ['Zillow']
    sites_list: List[SiteSchema] = get_sites_list(cli_options)
    assert len(sites_list) == 1


def test_generate_username_sites() -> None:
    cli_options: CliOptionsSchema = get_default_cli_options()
    sites_list: List[SiteSchema] = get_sites_list(cli_options)
    count = len(sites_list)
    new_sites: List[SiteSchema] = generate_username_sites(['yooper', 'webbreacher'], sites_list)
    assert (count*2) == len(new_sites)


def test_generate_username_has_dot() -> None:
    cli_options: CliOptionsSchema = get_default_cli_options()
    sites_list: List[SiteSchema] = get_sites_list(cli_options)
    new_sites: List[SiteSchema] = generate_username_sites(['yoo.per'], sites_list)
    assert 421 == len(new_sites)


def test_filter_list_all() -> None:
    cli_options: CliOptionsSchema = get_default_cli_options()
    sites_list: List[SiteSchema] = get_sites_list(cli_options)
    cli_options.all = True
    results: List[SiteSchema] = filter_list_by(cli_options, sites_list)
    assert len(results) == len(sites_list)


def test_filter_list_by_category() -> None:
    cli_options: CliOptionsSchema = get_default_cli_options()
    cli_options.category = 'social'
    sites_list: List[SiteSchema] = get_sites_list(cli_options)
    cli_options.all = True
    results: List[SiteSchema] = filter_list_by(cli_options, sites_list)
    assert len(results) == len(sites_list)


def test_filter_found() -> None:
    cli_options: CliOptionsSchema = get_default_cli_options()
    cli_options.all = False
    sites_list: List[SiteSchema] = get_sites_list(cli_options)
    site: SiteSchema
    for site in sites_list:
        site.http_status_code = site.e_code

    results: List[SiteSchema] = filter_list_by(cli_options, sites_list)
    assert len(results) == len(sites_list)


def test_filter_not_found() -> None:
    cli_options: CliOptionsSchema = get_default_cli_options()
    sites_list: List[SiteSchema] = get_sites_list(cli_options)
    cli_options.all = False
    cli_options.not_found = True
    site: SiteSchema
    for site in sites_list:
        site.http_status_code = site.m_code

    results: List[SiteSchema] = filter_list_by(cli_options, sites_list)
    assert len(results) == len(sites_list)

