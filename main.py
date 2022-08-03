import asyncio
from typing import Dict, List

from whatsmyname.app.cli.args import get_default_args, arg_parser
from whatsmyname.app.models.enums.common import OutputFormat
from whatsmyname.app.models.schemas.cli import CliOptionsSchema
from whatsmyname.app.models.schemas.sites import SiteSchema
from whatsmyname.app.tasks.process import process_cli
from whatsmyname.app.utilities.formatters import to_json, to_csv, to_table


async def main():

    argparse = get_default_args()
    schema: CliOptionsSchema = arg_parser(argparse.parse_args())
    sites: List[SiteSchema] = await process_cli(schema)
    # filter the sites

    if schema.format == OutputFormat.JSON:
        to_json(sites, schema.output_file)
    elif schema.format == OutputFormat.CSV:
        to_csv(sites, schema.output_file)
    elif schema.format == OutputFormat.TABLE:
        to_table(sites, schema.output_file)

    if schema.output_stdout:
        with open(schema.output_file, 'r') as fp:
            lines: List[str] = fp.readlines()
            for line in lines:
                print('{}'.format(line.strip()))


if __name__ == "__main__":
    asyncio.run(main())
