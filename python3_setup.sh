#!/usr/bin/env bash

# copy this part out of https://confluence.diamond.ac.uk/x/GxKRBQ
# whenever it is updated
export PATH=/dls_sw/prod/python3/RHEL7-x86_64/dls_ade/2.0.0a4/prefix/bin:$PATH
export PIPENV_PYPI_MIRROR=http://pypi.diamond.ac.uk:8080

# Put all Pipenv virtualenvs into somewhere on scratch
export WORKON_HOME=/scratch/jjc62351/cache/pipenv

# workaround to a PIP problem https://github.com/pypa/pipenv/issues/3792
export PIP_NO_CACHE_DIR=false
# why is this not true by default?
export PYTHONPATH=.

# In the project directory you need to tell pipenv to use python 3.7. Run this commmand:
# pipenv --python /dls_sw/prod/tools/RHEL7-x86_64/Python3/3-7-2/prefix/bin/dls-python3.7
