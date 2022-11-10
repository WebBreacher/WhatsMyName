import logging
import os.path
import string
import tempfile
from argparse import ArgumentParser
from random import choice
from typing import List

from whatsmyname.app.config import project_path, resource_dir, main_dir
from whatsmyname.app.extractors.file_extractors import user_agent_extractor
from whatsmyname.app.models.schemas.cli import CliOptionsSchema
from whatsmyname.app.models.schemas.user_agent import UserAgentSchema

logger = logging.getLogger()


def get_default_args() -> ArgumentParser:
    """
    Returns an argument parser with a set of defaults
    :return:
    """
    parser = ArgumentParser(
        description="This standalone script will look up username using the JSON file"
                    " or will run a check of the JSON file for bad detection strings.")
    parser.add_argument('-u', '--usernames', nargs='*', help='[OPTIONAL] If this param is passed then this script will perform the '
                                                 'lookups against the given user name instead of running checks against '
                                                 'the JSON file.')
    parser.add_argument('-in', '--input_file', nargs='?',
                        help="[OPTIONAL] Uses a specified file for checking the websites")
    parser.add_argument('-s', '--sites', nargs='*',
                        help='[OPTIONAL] If this parameter is passed the script will check only the named site or list of sites.')
    parser.add_argument('-a', '--all', help="Display all results.", action="store_true", default=False)
    parser.add_argument('-n', '--not_found', help="Display not found results", action="store_true", default=False)
    parser.add_argument('-d', '--debug', help="Enable debug output", action="store_true", default=False)
    parser.add_argument('-o', '--output_file', nargs='?', help="[OPTIONAL] Uses a specified output file ")
    parser.add_argument('-t', '--timeout', nargs='?', help='[OPTIONAL] Timeout per connection, default is 60 seconds.', default=60)
    parser.add_argument('-prt', '--per_request_time', nargs='?', help='[Optional] Timeout per request, default is 15 seconds', default=15)
    parser.add_argument('-fmt', '--format', nargs='?', help='[Optional] Format options are json, csv, or table', default='table')
    parser.add_argument('-v', '--verbose', help="Enable verbose output", action="store_true", default=False)
    parser.add_argument('-fr', '--follow_redirects', help="Follow redirects", action="store_true", default=False)
    parser.add_argument('-mr', '--max_redirects', nargs='?', help='[OPTIONAL] Max Redirects, default is 10 ', default=10)
    parser.add_argument('-c', '--category', nargs='?', help='[OPTIONAL] Filter by site category ', default=None)
    parser.add_argument('-rv', '--random_validate', action="store_true", help='[OPTIONAL] Upon success, validate using random username', default=False)
    parser.add_argument('-ua', '--user_agent_id', nargs='?', help='[OPTIONAL] Select the user agent platform to use. ', default=1)
    return parser


def arg_parser(arguments: ArgumentParser) -> CliOptionsSchema:
    """
    Parse the passed in arguments into something the schema will understand
    :param arguments: ArgumentParser
    :return:
    """
    parsed = vars(arguments)
    schema: CliOptionsSchema = CliOptionsSchema(**parsed)

    # set global logger levels
    if schema.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    if schema.input_file and not os.path.isfile(schema.input_file):
        logger.error('Input file does not exist %s', schema.input_file)
        raise Exception(f'Input file does not exist ${schema.input_file}.')

    if not schema.input_file:
        input_file: str = os.path.join(main_dir, 'wmn-data.json')
        schema.input_file = input_file
        logger.debug('Loading default input file %s', input_file)

    if schema.output_file:
        schema.output_stdout = False

    if not schema.output_file:
        letters = string.ascii_lowercase
        schema.output_file = os.path.join(tempfile.gettempdir(), ''.join(choice(letters) for _ in range(10)))
        schema.output_stdout = True

    if schema.random_validate:
        logger.debug('Randomly generated username is %s', schema.random_username)

    if not schema.usernames:
        schema.validate_knowns = True

    user_agents: List[UserAgentSchema] = user_agent_extractor(os.path.join(resource_dir, 'user-agents.json'))
    schema.user_agent = next(obj.user_agent for obj in user_agents if obj.id == schema.user_agent_id)

    if not schema.user_agent:
        raise Exception('User agent platform %s does not exist', schema.user_agent)

    return schema



