"""Format the data and write it to a temporary file."""
from typing import List
import csv

from whatsmyname.app.models.schemas.cli import CliOptionsSchema
from whatsmyname.app.models.schemas.sites import SiteSchema, SiteOutputSchema


def to_csv(cli_options: CliOptionsSchema, sites: List[SiteSchema]) -> None:

    field_names: List[str] = ['http_status_code', 'generated_uri']
    if cli_options.verbose:
        field_names.append('raw_response_data')

    with open(cli_options.output_file, "w") as fp:
        writer = csv.DictWriter(fp, fieldnames=field_names)
        writer.writeheader()
        site: SiteSchema
        for site in sites:
            site_output: SiteOutputSchema = SiteOutputSchema(**site.dict())
            writer.writerow(site_output.dict())


def to_json(cli_options: CliOptionsSchema, sites: List[SiteSchema]) -> None:
    field_names = {'http_status_code': True, 'generated_uri': True}
    if cli_options.verbose:
        field_names['raw_response_data'] = True

    with open(cli_options.output_file, "w") as fp:
        fp.write("[")
        site: SiteSchema
        for site in sites:
            site_output: SiteOutputSchema = SiteOutputSchema(**site.dict())
            fp.write(site_output.json(include=field_names))
        fp.write("]")


def to_table(cli_options: CliOptionsSchema, sites: List[SiteSchema]) -> None:
    pass


