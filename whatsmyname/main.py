import asyncio
from typing import List

from whatsmyname.app.cli.args import get_default_args, arg_parser
from whatsmyname.app.config import random_username
from whatsmyname.app.models.enums.common import OutputFormat
from whatsmyname.app.models.schemas.cli import CliOptionsSchema
from whatsmyname.app.models.schemas.sites import SiteSchema
from whatsmyname.app.tasks.process import process_cli, filter_list_by, generate_username_sites, \
    request_controller, get_sites_list
from whatsmyname.app.utilities.formatters import to_json, to_csv, to_table


async def start_check_for_presence():

    argparse = get_default_args()
    cli_options: CliOptionsSchema = arg_parser(argparse.parse_args())
    sites: List[SiteSchema] = await process_cli(cli_options)

    # filter the sites
    sites = filter_list_by(cli_options, sites)

    if cli_options.random_validate:
        cli_options.usernames = [cli_options.random_username]
        sites = await process_cli(cli_options)

    if cli_options.format == OutputFormat.JSON:
        to_json(cli_options, sites)
    elif cli_options.format == OutputFormat.CSV:
        to_csv(cli_options, sites)
    elif cli_options.format == OutputFormat.TABLE:
        to_table(cli_options, sites)
        # further processing is not required for the table format
        exit(1)

    if cli_options.output_stdout:
        with open(cli_options.output_file, 'r') as fp:
            lines: List[str] = fp.readlines()
            for line in lines:
                print('{}'.format(line.strip()))


def check_for_presence() -> None:
    asyncio.run(start_check_for_presence())


def _validate_site(site: SiteSchema) -> None:
    code_match: bool = site.http_status_code == site.e_code
    # a site will return no response in some cases
    if not site.raw_response_data:
        site.error_hint = f'No response data from site. {site.e_string}'
        return

    string_match: bool = site.raw_response_data.find(site.e_string) >= 0
    if code_match and string_match:
        site.error_hint = None
    elif code_match and not string_match:
        site.error_hint = f'Bad Detection String {site.e_string}'
    elif not code_match and string_match:
        site.error_hint = f'Bad Detection Response Code. Received {site.http_status_code} Expected {site.e_code}.'
    else:
        site.error_hint = f'Bad Code and String'


async def start_validate_whats_my_name() -> None:
    """Validates if a site is returning a correct set of values for an unknown and a known user."""
    argparse = get_default_args()
    cli_options: CliOptionsSchema = arg_parser(argparse.parse_args())
    cli_options.add_error_hints = True
    cli_options.debug = True
    cli_options.verbose = True

    # for the first pass, we use a random user name
    cli_options.usernames = [random_username()]

    sites: List[SiteSchema] = \
        await request_controller(cli_options, generate_username_sites(cli_options.usernames, get_sites_list(cli_options)))

    # this is the set of sites that did match the expected criteria
    invalid_sites = list(filter(lambda site: site.http_status_code != site.m_code or site.m_string not in (site.raw_response_data or ''), sites))

    # retest these sites with a known user
    cli_options.sites = [site.name for site in invalid_sites]

    sites_with_known: List[SiteSchema] = []
    for site in invalid_sites:
        sites_with_known.extend(generate_username_sites([site.known[0]], [site]))

    # filter the sites
    sites = await request_controller(cli_options, sites_with_known)
    sites = list(filter(lambda site: site.http_status_code != site.e_code or site.e_string not in (site.raw_response_data or ''), sites))

    for site in sites:
        _validate_site(site)

    if cli_options.format == OutputFormat.JSON:
        to_json(cli_options, sites)
    elif cli_options.format == OutputFormat.CSV:
        to_csv(cli_options, sites)
    elif cli_options.format == OutputFormat.TABLE:
        to_table(cli_options, sites)
        # further processing is not required for the table format
        exit(1)

    if cli_options.output_stdout:
        with open(cli_options.output_file, 'r') as fp:
            lines: List[str] = fp.readlines()
            for line in lines:
                print('{}'.format(line.strip()))


def validate_whats_my_name() -> None:
    asyncio.run(start_validate_whats_my_name())
