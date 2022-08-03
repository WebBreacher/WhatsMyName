from argparse import ArgumentParser
from typing import Dict

import pytest

from whatsmyname.app.cli.args import arg_parser, get_default_args
from whatsmyname.app.models.schemas.cli import CliOptionsSchema
from whatsmyname.app.tasks.process import process_cli


def test_arg_parse_basic() -> None:

    args: ArgumentParser = get_default_args()
    schema: CliOptionsSchema = arg_parser(args.parse_args(['-u', 'yooper', '-d']))
    assert schema.debug


def test_arg_parse_sites() -> None:

    args: ArgumentParser = get_default_args()
    schema: CliOptionsSchema = arg_parser(args.parse_args(['-d', '--sites', '3DNews', 'CNN', '-u', 'yooper']))
    assert schema.debug
    assert schema.sites == ['3DNews', 'CNN']
    assert schema.usernames == ['yooper']


@pytest.mark.asyncio
async def test_arg_parse_all() -> None:
    args: ArgumentParser = get_default_args()
    schema: CliOptionsSchema = arg_parser(args.parse_args(['-u', 'yooper', '--sites', 'allesovercrypto']))
    results: Dict[str, int] = await process_cli(schema)
    assert len(results) == 1
