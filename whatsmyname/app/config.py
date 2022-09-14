import os
import string
from pathlib import Path
import random

project_path = os.path.dirname(os.path.realpath(__file__))
resource_dir = os.path.join(project_path, 'resources')
main_dir = Path(__file__).parent.parent.parent


def random_username(length: int = 8) -> str:
    return ''.join(
        random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for x in range(length))
