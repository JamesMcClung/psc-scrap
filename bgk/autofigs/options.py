# Parameters that affect all figures
SETTINGS = ["nframes", "slice", "periodic", "output_directory"]

# Parameters that affect other settings
METASETTINGS = ["suite"]

# Types of figures that can be specified by a single string, e.g. "ne"
TRIVIAL_FIGURE_TYPES = ["videos", "profiles", "stabilities", "origin_means", "periodograms", "extrema"]

# Types of figures that require more than just a string, e.g. ["ne", "prt:v_phi"]
NONTRIVIAL_FIGURE_TYPES = ["sequences"]

# All figure types
FIGURE_TYPES = TRIVIAL_FIGURE_TYPES + NONTRIVIAL_FIGURE_TYPES
