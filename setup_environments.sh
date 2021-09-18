#!/bin/sh
for dir in "energy_detection" "dummy"
do
    dir=${dir%*/}
    if [ -f $dir/requirements.txt ]; then
        if [ -d $dir/${dir}_env ]; then
            rm -rf $dir/${dir}_env
        fi
        echo Creating $dir/${dir}_env
        python3 -m venv $dir/${dir}_env
        echo Installing requirements for ${dir}
        $dir/${dir}_env/bin/pip3 install wheel
        $dir/${dir}_env/bin/pip3 install setuptools
        $dir/${dir}_env/bin/pip3 install scikit-build
        $dir/${dir}_env/bin/pip3 install Cython
        $dir/${dir}_env/bin/pip3 install numpy
        $dir/${dir}_env/bin/pip3 install -r $dir/requirements.txt
        if [ -f $dir/requirements_git.txt ]; then
          # $dir/${dir}_env/bin/pip3 install numpy
          # $dir/${dir}_env/bin/pip3 install pandas
          # $dir/${dir}_env/bin/pip3 install cython
          # $dir/${dir}_env/bin/pip3 install astropy
          # $dir/${dir}_env/bin/pip3 install matplotlib
          # $dir/${dir}_env/bin/pip3 install scipy
          # $dir/${dir}_env/bin/pip3 install pytest
          # $dir/${dir}_env/bin/pip3 install dask xarray
          # $dir/${dir}_env/bin/pip3 install turbo-seti
          $dir/${dir}_env/bin/pip3 install -r $dir/requirements_git.txt
        fi
    fi
done
