# pcds-envs

A simple repo to hold our current and past conda environment.yaml files. Each yaml file is the most recent version of an environment of a specific type. The `pcds.yaml` file is designated as the 'catch-all' for generic python sessions, but individual apps may want to create app-specific environments.

Usage:

- `make_base_env.sh` is a quick script for building a "latests" environment
- Create a new yaml file as `conda env export -n envname -f filename`
- Load a yaml file with `conda env create -n envname -f filename`

So, to make a new release of `pcds.yaml`, from my checkout I run:
```
git checkout -b rel-1.2.3
./make_base_env.sh pcds-1.2.3
conda env export -n pcds-1.2.3 -f pcds.yaml
git add pcds.yaml
git commit -m "ENH: updated yaml to 1.2.3"
git push origin rel-1.2.3
```
Then on github I make a PR, after which I update the central checkout and `conda env create -n pcds-1.2.3 -f pcds.yaml`

You can follow a similar procedure for any app-specifc environment you'd like to implement.
