git remote add dev git@github.com:UCBerkeleySETI/BL-Reservoir.git
git fetch --all --tags
git checkout tags/dev
cd /code
python3 -m bl_reservoir.server
