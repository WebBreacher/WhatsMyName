import os
from pathlib import Path

project_path = os.path.dirname(os.path.realpath(__file__))
resource_dir = os.path.join(project_path, 'resources')
main_dir = Path(__file__).parent.parent.parent
