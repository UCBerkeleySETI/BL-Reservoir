cd /code
git clone https://github.com/UCBerkeleySETI/BL-Reservoir latest
cd latest
git fetch --all --tags
git checkout tags/dev
cd /code
python3 -m latest.server
