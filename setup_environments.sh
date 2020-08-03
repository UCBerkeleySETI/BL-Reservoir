#!/bin/sh
for dir in */
do
    dir=${dir%*/}
    if [ -f $dir/requirements.txt ]; then
        if [ -d $dir/${dir}_env ]; then
            rm -rf $dir/${dir}_env
        fi
        echo Creating $dir/${dir}_env
        python3 -m venv $dir/${dir}_env
        echo Installing requirements for ${dir}
        $dir/${dir}_env/bin/pip3 install -r $dir/requirements.txt
        if [ -f $dir/requirements_git.txt ]; then
          $dir/${dir}_env/bin/pip3 install -r $dir/requirements_git.txt
    fi
done
