# Readme

## Autofigs

The main feature is `autofigs.py`, a script that automatically generates figures. The figures it generates are configured by an input yaml file, which is `autofigs.yml` if unspecified. The details of these yaml files aren't important for now; it suffices to know that they specify which figures to generate for which runs.

The most basic use of `autofigs.py` is the following, which attempts to load `autofigs.yml` and generate the figures specified therein:
```bash
python autofigs.py
```

A different configuration yaml can be specified as an argument:
```bash
python autofigs.py some_other_autofigs.yml
```

### Flags

Autofigs supports a number of flags. Any argument that starts with a "-" is interpreted as a flag; the number of "-"s doesn't actually matter. Arguments to flags are concatenated to the end of the flag, separated by "=" (with no spaces in between).

| Flag     | Argument    | Description                                                                                                                |
| :------- | :---------- | :------------------------------------------------------------------------------------------------------------------------- |
| `--save` | —           | Adds the specified figures to an ever-growing `autofigs.history.yml`                                                       |
| `--warn` | —           | At runtime, asks for confirmation if a figure would be made with different parameters than found in `autofigs.history.yml` |
| `--only` | figure type | Only generates figures of the specified type (see [Yaml Configuration](#yaml-configuration) for the figure types)          |

For example, to recreate all movies (which you might do if you changed how movies are generated and want to update existing figures), you could run:
```bash
python autofigs.py autofigs.history.yml --only=videos
```

If you're generating some important figures for the first time (and specified them in the usual `autofigs.yml`), you should run:
```bash
python autofigs.py --save --warn
```

There is currently no way of removing figure specifications from `autofigs.history.yml` other than manually editing the file, so only use `--save` when you're sure your specifications are correct and worth saving. The `--warn` flag can help prevent mistakes by giving you a chance to verify a conflicting spec before the figure is generated, exiting the program if you decide the spec was wrong. Importantly, **history isn't saved until *all* figures have been generated**: if you exit the program early, for any reason, history won't be saved.

### Yaml Configuration

Autofig configuration files are written in yaml. At a minimum, the yaml object must have an `instructions` field with a list of objects. The table below describes the fields each object can have. Fields lacking a default value are required.

| Field              | Value Type               | Default Value | Description                                                                                  |
| :----------------- | :----------------------- | :------------ | :------------------------------------------------------------------------------------------- |
| `path`             | `string` (absolute path) | —             | Where to find run data.                                                                      |
| `output_directory` | `string` (absolute path) | —             | Where to put generated figures.                                                              |
| `nframes`          | `int`                    | —             | How many timesteps to load and use for figure generation. Steps are evenly spaced.           |
| `periodic`         | `boolean`                | —             | Whether to treat the run as periodic, only generating certain figures over the first period. |
| `slice`            | `"whole" \| "center"`    | —             | How much of the domain to consider for figure generation.                                    |
| `prefix`           | `string`                 | `""`          | Prepended to the generated figure file name.                                                 |
| `suite`            | `string \| None`         | `None`        | Optional suite to supply unspecified values.                                                 |
| `extrema`          | `list[FieldVariable]`    | `[]`          | List of extrema plots to generate for the run.                                               |
| `origin_mean`      | `list[FieldVariable]`    | `[]`          | List of origin mean plots to generate for the run.                                           |
| `profiles`         | `list[FieldVariable]`    | `[]`          | List of profile plots to generate for the run.                                               |
| `periodogram`      | `list[FieldVariable]`    | `[]`          | List of periodograms to generate for the run.                                                |
| `stability`        | `list[FieldVariable]`    | `[]`          | List of stability plots to generate for the run.                                             |
| `sequences`        | `list[list[Variable]]`   | `[]`          | List of sequences to generate for the run.                                                   |
| `videos`           | `list[Variable]`         | `[]`          | List of videos to generate for the run.                                                      |

In the table above, `FieldVariable` represents any string corresponding to the name of a `FieldVariable` instance in `bgk/field_variables.py`, e.g. `"ne"`. While not explicit in the table, `ParticleVariable` represents any string corresponding to the name of a `ParticleVariable` instance in `bgk/particle_variables.py` and prepended with `"prt:"`, e.g. `"prt:v_phi"`. The `Variable` type is the union of `FieldVariable` and `ParticleVariable`. See [Variables](#variables) for more information on what these variables are and how to customize them.

#### Suites

A configuration file can also have a toplevel `suites` item, which is just like `instructions` except it stores a dict of objects instead of a list. The objects in `suites` are simply named templates that can be referred to in the `suite` field of objects in `instructions`. Each field from a suite becomes the default value for fields of the `instruction` object.

> ###### Yaml Configuration: A Walkthrough
>
> ```yml
> instructions:
>   - path: /absolute/path/to/run1
>     output_directory: /absolute/path/to/figs/
>     nframes: 101
>     periodic: true
>     slice: whole
>     videos: [ne]
>     profiles: [e_rho]
>     sequences: [[ne, prt:v_phi]]
>   - path: /absolute/path/to/run2
>     output_directory: /absolute/path/to/figs/
>     nframes: 11
>     periodic: false
>     slice: center
>     videos: [ne, e_phi]
> ```
> 
> The `instructions` field is a list of objects, where each object specifies figures for a particular run. The example above will make a total of five figures across two different runs:
> - A video of electron density (`ne`) with 101 frames from run1
> - A plot of the mean radial component of the electric field (`e_rho`) vs. rho with 101 data points from run1
> - An image with two parallel sequences of images from run1—electron density on the top, and the reduced distribution function f(v_phi, rho) (`prt:v_phi`) on the bottom—over the course of one oscillation
> - A zoomed-in video of electron density with 11 frames from run2
> - A zoomed-in video of the azimuthal component of the electric field with 11 frames from run2
> All of these figures are saved to `/absolute/path/to/figs/` with automatically generated names.
>
> See `autofigs_template.yml` for a more realistic example, including a suite.

### Customization

The figures generated by `autofigs.py` can be customized in a number of ways.

#### Variables

Variables are instances of the `Variable` class, found in `bgk/variable.py`. A variable is essentially a recipe for turning data into a figure. For example, the `ne` variable in `bgk/field_variables.py` describes how to turn data from a `pfd_moments.*.bp` file into a visual representation of electron number density. More variables can be found in `bgk/particle_variables.py`, which deal with data in `prt.*.h5` files.

#### Figures

Simple figure generators can be easily added. The recommended way of doing so is to copy how it is done for existing figure generators, such as `bgk/autofigs/figure_generators/stability.py`:
1. Create a file in `bgk/autofigs/figure_generators/`
2. Write a function with the same signature as other figure generators
3. Annotate the function with `@figure_generator(name)`, where `name` is a string corresponding to the name of the figure as it will appear in both output `.png` files and configuration `.yml` files
4. Import the file or function in `bgk/autofigs/figure_generators/__init__.py`

The annotation will automatically make the function known to `autofigs.py` with the given name, provided it is imported. Currently, these figure generators can only depend on field data, not particle data.

#### Snapshots

More complex figure types (i.e., videos and sequences) use "snapshot generators" to turn data at specific timesteps into a visual representation, and combine such representations into one figure. Snapshot generators are slightly more complex than figure generators, but they are added in a similar way. See `bgk/autofigs/snapshot_generators/image.py` for an example.

The main complication is in respecting the `set_data_only` parameter in `SnapshotParams`. This boolean is true when the figure maker draws on the same axes multiple times, such as in `bgk/autofigs/movie.py`. It is important to not keep adding artists to the axes, or else figure generation will slow down immensely and may have noticeable consequences for the resulting figure.

Currently, `FieldVariable` variables are hardcoded to use the `image` snapshot generator, and `ParticleVariable` variables are hardcoded to use `histogram`. This will change in the future and necessitate an API change.
