"""Format the data and write it to a temporary file."""
from typing import List
import csv

from whatsmyname.app.models.schemas.cli import CliOptionsSchema
from whatsmyname.app.models.schemas.sites import SiteSchema, SiteOutputSchema
from terminaltables import AsciiTable


def to_csv(cli_options: CliOptionsSchema, sites: List[SiteSchema]) -> None:

    field_names: List[str] = ['name', 'category', 'http_status_code', 'generated_uri', 'username']
    if cli_options.verbose:
        field_names.append('raw_response_data')
        field_names.append('user_agent')
        field_names.append('response_headers')

    if cli_options.add_error_hints:
        field_names.append('error_hint')

    with open(cli_options.output_file, "w") as fp:
        writer = csv.DictWriter(fp, fieldnames=field_names)
        writer.writeheader()
        site: SiteSchema
        for site in sites:
            site_output: SiteOutputSchema = SiteOutputSchema(**site.dict())
            writer.writerow(site_output.dict(include=dict.fromkeys(field_names, True)))


def to_json(cli_options: CliOptionsSchema, sites: List[SiteSchema]) -> None:
    field_names = {'name': True, 'category': True, 'http_status_code': True, 'generated_uri': True, 'username': True}
    if cli_options.verbose:
        field_names['raw_response_data'] = True
        field_names['user_agent'] = True
        field_names['response_headers'] = True

    if cli_options.add_error_hints:
        field_names['error_hint'] = True

    with open(fix_file_name(cli_options.output_file), "w") as fp:
        fp.write("[")
        site: SiteSchema
        for idx, site in enumerate(sites):
            site_output: SiteOutputSchema = SiteOutputSchema(**site.dict())
            fp.write(site_output.json(include=field_names))
            if idx < len(sites) - 1:
                fp.write(",")
        fp.write("]")


def fix_file_name(file_name: str) -> str:
    return file_name.encode('ascii', 'ignore').decode('ascii')


def to_table(cli_options: CliOptionsSchema, sites: List[SiteSchema]) -> None:
    """Output a table to the terminal"""
    table_data: List[List[str]] = [
        ['Site Name', 'Url', 'Category', 'Result']
    ]

    if cli_options.add_error_hints:
        table_data[0].append('Error Hint')

    for site in sites:
        pretty_url = site.uri_pretty.replace("{account}", site.username) if site.uri_pretty else site.generated_uri
        pretty_url = pretty_url[0:cli_options.word_wrap_length]
        row = [site.name, pretty_url, site.category, site.http_status_code]
        if cli_options.add_error_hints:
            row.append(site.error_hint if site.error_hint else '')
        table_data.append(row)

    table = AsciiTable(table_data)
    with open(fix_file_name(cli_options.output_file), "w") as fp:
        fp.write(table.table)
        fp.write("\n")



