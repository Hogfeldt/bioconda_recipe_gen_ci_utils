#!/bin/bash

###############################################
# Cron wrapper for testing Bioconda-recipe-gen
###############################################

##### Constants

REPO=https://github.com/Hogfeldt/bioconda_recipe_gen.git
NAME=$(basename "$REPO" .git)
CONDA_DEPS="bioconda-utils docker-py"
PACKAGES=("kallisto" "tn93" "htstream" "qfilt" "libdivsufsort" "clever-toolkit")
BASE_PATH=/home/per/bioconda_recipe_gen_cron_tests
TEST_DIR=$BASE_PATH/$(date +%Y%m%d)
META_FILE=$TEST_DIR/test_meta.txt

#####

if [ -d $TEST_DIR ]; then
    exit 1
fi
cd $BASE_PATH

# TODO:
# pull latest repository
git clone $REPO
cd $NAME
# setup environment
conda create --yes -n "$NAME" python=3.6 
# the line below can only be done by root on server
#conda config --add channels conda-forge
#conda config --add channels bioconda
#conda update --yes conda

source /opt/conda/bin/activate "$NAME"
conda install --yes $CONDA_DEPS

# install software
python setup.py develop
git clone https://github.com/bioconda/bioconda-recipes

mkdir $TEST_DIR
echo git_commit_sha: $(git rev-parse HEAD) >> $META_FILE
echo start_time: $(date) >> $META_FILE
# run all cases and save the result of each case. 
for package in ${PACKAGES[*]}
do
    ./travis/test.sh $package &> $TEST_DIR/$package.out
    status=$? # store exit code
    if [ $status -eq 0 ]; then 
        echo "$package build succeded" >> $META_FILE  
    else
        echo "$package build failed" >> $META_FILE
    fi
done
echo end_time: $(date) >> $META_FILE

# send mail with result

# Clean up environment
conda deactivate
conda env remove --yes --name "$NAME"                                     

# Remove bioconda_recipe_gen
cd $BASE_PATH
rm -rf "$NAME"
