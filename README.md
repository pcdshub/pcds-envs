# pcds-envs

A simple repo to hold our current and past conda environment.yaml files. Each yaml file is the most recent version of an environment of a specific type. The `pcds.yaml` file is designated as the 'catch-all' for generic python sessions, but individual apps may want to create app-specific environments.

To use a built environment:
- Find the conda landing area `/reg/g/pcds/pyps/conda`
- For latest: `source py36env.sh`
- For specific: `source py36env.sh pcds-0.1.0`

To create a development environment from a yaml:
- Download and install a [miniconda environment](https://conda.io/miniconda.html)
- `git clone https://github.com/pcdshub/pcds-env.git`
- `cd pcds-env`
- optional: `git fetch`, `git checkout 0.1.0` (if you'd like a tag other than latest)
- `conda env create -n myenvname -f pcds.yaml`

To manage releases:
- `stage_release.sh <relnum> <name>`: creates a git branch, builds an environment, updates yaml, pushes to origin
- `apply_release.sh <relnum> <name>`: checks out a tag, reads a yaml file, locks down write-access

So, to make a new release of `pcds.yaml`, from my checkout I run:
```
./stage_release.sh 1.2.3
```
Then I go to github and make a PR with my rel-1.2.3 branch.
After we decide to merge it, I tag a `1.2.3` release and go to the release area:
```
cd /reg/g/pcds/pyps/conda
source py36env.sh
cd pcds-envs/scripts
./apply_release.sh 1.2.3
```
You can follow a similar procedure for any app-specifc environment you'd like to implement, but pass a `<name>` argument to the scripts and pre-build the environment you want. Here is an example, **assuming I've already built an ``ease-0.1.0`` environment**:
```
cd my_checkout/scripts
./stage_releash.sh 0.1.0 ease
```
Then go to github and justify your PR. Once merged, create an `ease-0.1.0` tag (not a release) and go to the checkout:
```
cd /reg/g/pcds/pyps/conda
source py36env.sh
cd pcds-envs/scripts
./apply_release.sh 0.1.0 ease
```
