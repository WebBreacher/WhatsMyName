import asyncio
import os
import tempfile
from typing import List

from whatsmyname.app.cli.args import get_default_args, arg_parser
from whatsmyname.app.config import random_username
from whatsmyname.app.models.enums.common import OutputFormat
from whatsmyname.app.models.schemas.cli import CliOptionsSchema
from whatsmyname.app.models.schemas.sites import SiteSchema
from whatsmyname.app.tasks.process import process_cli, filter_list_by, capture_errors, generate_username_sites, \
    request_controller
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

    if cli_options.output_stdout and not cli_options.capture_errors:
        with open(cli_options.output_file, 'r') as fp:
            lines: List[str] = fp.readlines()
            for line in lines:
                print('{}'.format(line.strip()))

    if cli_options.capture_errors:
        capture_errors(cli_options, sites)


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
    argparse = get_default_args()
    cli_options: CliOptionsSchema = arg_parser(argparse.parse_args())
    cli_options.add_error_hints = True
    cli_options.debug = True
    cli_options.verbose = True
    cli_options.capture_errors = True
    sites: List[SiteSchema] = await process_cli(cli_options)

    # filter the sites
    sites = filter_list_by(cli_options, sites)

    for site in sites:
        _validate_site(site)

    revalidate_sites: List[SiteSchema] = list(filter(lambda site: site.error_hint is None, sites))
    errored_sites: List[SiteSchema] = list(filter(lambda site: site.error_hint, sites))

    # reset site fields
    for site in revalidate_sites:
        site.http_status_code = -1
        site.username = None
        site.raw_response_data = None
        site.generated_uri = None

    # unique the revalidate list
    seen = set()
    unique_sites: List[SiteSchema] = []
    for site in revalidate_sites:
        if site.name not in seen:
            unique_sites.append(site)
            seen.add(site.name)

    validated_sites = await request_controller(cli_options, generate_username_sites([random_username()], unique_sites))
    for site in validated_sites:
        _validate_site(site)

    sites = errored_sites
    sites.extend(validated_sites)

    if cli_options.format == OutputFormat.JSON:
        to_json(cli_options, sites)
    elif cli_options.format == OutputFormat.CSV:
        to_csv(cli_options, sites)
    elif cli_options.format == OutputFormat.TABLE:
        to_table(cli_options, sites)
        # further processing is not required for the table format
        exit(1)

    if cli_options.output_stdout and not cli_options.capture_errors:
        with open(cli_options.output_file, 'r') as fp:
            lines: List[str] = fp.readlines()
            for line in lines:
                print('{}'.format(line.strip()))


def validate_whats_my_name() -> None:
    asyncio.run(start_validate_whats_my_name())
