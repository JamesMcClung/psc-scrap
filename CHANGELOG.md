# Changelog
Versions are tagged in git. Versioning follows [semantic versioning](https://semver.org/). The API is considerd to include:
- The autofigs yaml configuration format
- The figures generated by autofigs (where a patch-level change would not affect the information a figure contains [i.e., a formatting change], and a minor-level change would increase the information)

##### Change Categories
| Category      | Version Level  | Description                                                                           |
| :------------ | :------------- | :------------------------------------------------------------------------------------ |
| Documentation | Patch          | Changes to documentation, such as this changelog or the readme.                       |
| Internal      | Patch          | Internal changes that don't affect input, output, or runtime behavior.                |
| Tweaks        | Patch          | Changes that might affect runtime behavior, but not input or output.                  |
| Fixes         | Patch          | Bug fixes.                                                                            |
| Figures       | Any            | Changes or additions to figure generation.                                            |
| Config        | Minor or Major | Changes or additions to yaml configuration (other than addition of new figure types). |

## v0.3.0
_June 17, 2024_

Documentation
- Updated README to reflect how history is now saved

Config
- History now saves to a unique `.history.yml` file for each config file
- History files also now always include `prefix`, even when omitted from original config file

Internal
- Added `bgk/autofigs/config.py`, consolidating/facilitating handling of yaml configuration
- `bgk/autofigs/options.py`: split up `SETTINGS` global into several global lists/dicts

## v0.2.1
_June 4, 2024_

Internal
- `bgk/backend/wrapper_h5.py`:
    - Added `restrict` method, enabling dropping data based on a variable's value
    - Added docstrings to public interface
    - Renamed `col` method to `get`
    - Renamed `drop_columns` method to `drop_variables`
    - Renamed `_has_col` method to `_has_variable`
    - Renamed `_df` field to `_data`

## v0.2.0
_April 22, 2024_

Figures
- Removed `val_bounds` of velocity (and momentum) variables, since they assumed a particular temperature and aren't even necessary

Internal
- `bgk/params_record.py`:
    - Added more params: `k`, `h0`, `xi`, `A_x0`, `beta`

## v0.1.2
_April 16, 2024_

Fixes
- `autofigs.py`:
    - Field variables of videos are now detected as such

Documentation
- `CHANGELOG.md`:
    - Added forgotten tweak in v0.1.0

## v0.1.1
_April 16, 2024_

Documentation
- Added `CHANGELOG.md`
    - You're reading it
    - Retroactively wrote changes for past commits and added version tags
- `README.md`:
    - Cleaned up "Flags" section
    - Updated "Yaml Configuration" section to reflect new API and terminology (i.e. "variables")
        - These changes were from commits before v0.0.0
    - Added "Customization" section

## v0.1.0
_April 16, 2024_

Config
- `videos` option now supports `ParticleVariable` identifiers, prefixed with `prt:`

Tweaks
- `bgk/input_reader.py`:
    - If `path_input` points to `*psc/inputs/bgk/*` and it isn't there, guess that it can now be found at `*psc-scrap/inputs/*`
- `bgk/movie.py`:
    - Prints frame number during figure generation

Internal
- `bgk/movie.py`:
    - `make_movie`:
        - Added `SnapshotParams` param, subsuming old `FieldData` param
        - Added `nframes` param, required to match `data.nframes` if present (which it might not be, since `FieldData` has `nframes` field but `ParticleData` doesn't)
- `bgk/autofigs/snapshot_generator.py`:
    - `SnapshotParams`:
        - Now generic over `data` field, replacing old `fields` field
        - Added `set_data_only` field, to indicate that the snapshot has been generated once before, and now only existing aritists should be updated
        - Replaced `frame` field with `step`
    - `draw_snapshot` now returns list of artists
- Renamed `bgk/autofigs/snapshot_generators/map.py` to `bgk/autofigs/snapshot_generators/image.py`:
    - Now respects `set_data_only`
- `bgk/particle_data.py`:
    - Added `set_variable` method and `variable` field (no caching related to this, just to match `FieldData` interface)
    - Added `col` method
    - Added `run_manager` field and init param, subsuming `path` field and init param
    - Added `params_record` property, subsuming `inputFile`, `B`, `maxStep`, and `reversed` fields
    - Added `set_step` method and `step` field, used for caching
    - Replaced `t` field with `time` cached property
    - Replaced `_data` field with `data` cached property
    - Made `input` field a cached property
    - Removed `plot_distribution` (replaced by `draw_histogram` snapshot generator)
- `bgk/field_data.py`:
    - Make `params_record` a property
- Added `bgk/autofigs/snapshot_generators/histogram.py`:
    - Contains `draw_histogram` snapshot generator, which plots a particle variable vs. rho
- `bgk/autofigs/sequence.py`:
    - Added `plot_row` method generic over `params` and `snapshot_generator` params, subsuming `plot_row_prt` and `plot_row_pfd`
- `bgk/autofigs/options.py`:
    - `TRIVIAL_FIGURE_TYPES` now includes registered `FigureGenerator` names, but not `videos`

## v0.0.6
_April 3, 2024_

Tweaks
- Added `inputs/*`
    - Currently contains input files from case1, case2, and case4
- `make_params.py`:
    - Changed `path_to_data` to use inputs in `inputs/`

## v0.0.5
_April 2, 2024_

Internal
- `.gitignore`:
    - Don't ignore `autofigs_work.yml`

## v0.0.4
_April 2, 2024_

Internal
- Added `bgk/variable.py`
    - Contains `Variable` superclass
- `bgk/field_variables.py`:
    - `FieldVariable` is now a subclass of `Variable`
- `bgk/particle_variables.py`:
    - `ParticleVariable` is now a subclass of `Variable`
- `bgk/run_manager.py`:
    - `get_frame_manager` and various `FrameManager` initializers now take any `Variable`s, not just `FieldVariable`s

## v0.0.3
_April 2, 2024_

Internal
- `bgk/autofigs/figure_generator.py`:
    - Renamed `image_path_name` param to `figure_name`
    - Renamed `generate_image` method to `generate_figure` and field to `_generator`, and fixed method signature
- Added `bgk/autofigs/snapshot_generator.py`:
    - Contains `SnapshotParams` class, `SnapshotGenerator` class, `snapshot_generator` decorator, and `SNAPSHOT_GENERATOR_REGISTRY` global variable
    - "Snapshots" use data from a single timestep, in contrast to "figures" which use data from the entire run (some figures are made up of snapshots)
- Added `bgk/autofigs/snapshot_generators/map.py`:
    - Contains `draw_map` snapshot generator, which takes field data and turns it into a movie frame
        - This is currently the only snapshot generator
- `bgk/autofigs/movie.py`:
    - Removed `view_frame` and its helper functions, replaced by `draw_map` snapshot generator
    - `make_movie` takes a snapshot generator instead (i.e., `draw_map`)
- `bgk/autofigs/sequence.py`:
    - Renamed `videoMaker` variable/param to `field_data`
    - `plot_row_pfd` now takes a snapshot generator (i.e., `draw_map`)

## v0.0.2
_April 2, 2024_

Internal
- `bgk/autofigs/movie.py`:
    - Renamed `videoMaker` variable/param to `field_data`
    - Changed `view_frame` signature (so it can be called in animation loop)

## v0.0.1
_April 2, 2024_

Fixes
- `bgk/input_reader.py`:
    - `get_radius_of_structure` now detects and handles bump configurations
- `bgk/field_data.py`:
    - Fixed cache hit detection in `set_variable` always failing
- `bgk/util/safe_cache_invalidation`:
    - Fixed cache detection causing field to be initialized

Tweaks
- `bgk/run_manager.py`:
    - Changed `print_coverage` grammar

## v0.0.0
_March 28, 2024_

Version number of the last release before versioning started.