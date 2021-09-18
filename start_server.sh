git fetch --all --tags --prune
git checkout tags/dev
python3 -m bl_reservoir.server
