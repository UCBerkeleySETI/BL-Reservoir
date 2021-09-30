git fetch --all --tags --prune
git checkout tags/dev
cd /code
python3 -m bl_reservoir.server
