from . import figure_generators as _
from .figure_generator import FIGURE_GENERATOR_REGISTRY

# Parameters that affect figure generation
FIGURE_SETTINGS = ["nframes", "slice", "periodic"]

# Parameters that affect how figures are saved
SAVE_SETTINGS = ["output_directory", "prefix"]

# Parameters that affect other settings
METASETTINGS = ["suite"]

# Types of figures that can be specified by a single string, e.g. "ne"
TRIVIAL_FIGURE_TYPES = list(FIGURE_GENERATOR_REGISTRY.keys())

# Types of figures that require special variable parsing
NONTRIVIAL_FIGURE_TYPES = ["sequences", "videos"]

# All figure types
FIGURE_TYPES = TRIVIAL_FIGURE_TYPES + NONTRIVIAL_FIGURE_TYPES
