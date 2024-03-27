import sys
import dotenv

sys.path.append(dotenv.dotenv_values()["PYTHONPATH"])

from . import typing
from .field_data import *
from .input_reader import *
from .particle_data import *
from .backend import *
from .bounds import *
from . import field_variables
from .field_variables import FieldVariable
from . import particle_variables
from .particle_variables import ParticleVariable
from .params_record import *
from .run_manager import *

from . import autofigs
