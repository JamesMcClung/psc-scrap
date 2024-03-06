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

Autofigs supports a number of flags as well. Because I was lazy, any argument that starts with a "-" is interpreted as a flag, and the number of "-"s doesn't actually matter. Arguments to flags are appended to the end of the flag, separated by "=" (with no spaces in between).

| Flag   | Argument    | Description                                                                                |
| :----- | :---------- | :----------------------------------------------------------------------------------------- |
| --save | —           | Adds the specified figures to an ever-growing `autofigs.history.yml`                       |
| --warn | —           | Ask for confirmation if a figure in `autofigs.history.yml` would be made differently       |
| --only | figure type | Only generates figures of the specified type (see Yaml Configuration for the figure types) |

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

| Field              | Value Type                        | Default Value | Description                                                                                  |
| :----------------- | :-------------------------------- | :------------ | :------------------------------------------------------------------------------------------- |
| `path`             | string (absolute path)            | —             | Where to find run data.                                                                      |
| `output_directory` | string (absolute path)            | —             | Where to put generated figures.                                                              |
| `nframes`          | int                               | —             | How many timesteps to load and use in figure generation. Steps are evenly spaced.            |
| `periodic`         | boolean                           | —             | Whether to (attempt to) treat the run as periodic. Affects profiles, extrema, and sequences. |
| `slice`            | `"whole"` or `"center"`           | —             | How much of the domain to consider for figure generation.                                    |
| `prefix`           | string                            | `""`          | Prepended to the generated figure file name.                                                 |
| `suite`            | string                            | `None`        | Optional suite to supply unspecified values.                                                 |
| `videos`           | list\[Param\]                     | `[]`          | List of videos to generate for the run.                                                      |
| `profiles`         | list\[Param\]                     | `[]`          | List of profile plots to generate for the run.                                               |
| `stabilities`      | list\[Param\]                     | `[]`          | List of stability plots to generate for the run.                                             |
| `origin_means`     | list\[Param\]                     | `[]`          | List of origin mean plots to generate for the run.                                           |
| `periodograms`     | list\[Param\]                     | `[]`          | List of periodograms to generate for the run.                                                |
| `extrema`          | list\[Param\]                     | `[]`          | List of extrema plots to generate for the run.                                               |
| `sequences`        | list\[list\[Param or PrtParam\]\] | `[]`          | List of sequences to generate for the run.                                                   |

In the table above, Param and PrtParam are strings that refer to data from `pfd`/`pfd_moment`/`gauss` and `prt` files, respectively. Values for Param correspond to the constants defined in `bgk/field_variables.py`, e.g. `"ne"`. Values for PrtParam correspond to the valid parameters of `ParticleReader.plot_distribution` in `bgk/particle_reader.py`, but prepended with `"prt:"`, e.g. `"prt:v_phi"`.

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
