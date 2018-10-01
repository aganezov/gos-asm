#!/usr/bin/env bash

if [ "$TRAVIS_OS_NAME" = 'osx' ]; then
    brew update
    brew install wget
    if [[ "$PYTHON" == "2.7" ]]; then
      wget https://repo.continuum.io/miniconda/Miniconda2-latest-MacOSX-x86_64.sh -O miniconda.sh;
    else
      wget https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -O miniconda.sh;
    fi
    bash miniconda.sh -b -p $HOME/miniconda
    export PATH="$HOME/miniconda/bin:$PATH"
    hash -r
    conda config --set always_yes yes --set changeps1 no
    conda update -q conda
    # Useful for debugging any issues with conda
    conda info -a
    conda create -n test-environment python=$PYTHON
fi

if [ "$TRAVIS_OS_NAME" = 'linux' ]; then
    if [[ "$TRAVIS_PYTHON_VERSION" == "2.7" ]]; then
      wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -O miniconda.sh;
    else
      wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh;
    fi
    bash miniconda.sh -b -p $HOME/miniconda
    export PATH="$HOME/miniconda/bin:$PATH"
    hash -r
    conda config --set always_yes yes --set changeps1 no
    conda update -q conda
    # Useful for debugging any issues with conda
    conda info -a
    conda create -n test-environment python=$TRAVIS_PYTHON_VERSION
fi

source activate test-environment
conda install gcc
conda install make
conda install cmake
conda install git
git clone --single-branch -b gos-asm https://github.com/compbiol/mgra.git
cd mgra
mkdir build
cmake ../
make
export MGRA_PATH="$HOME/mgra/build/src/mgra/indel_mgra"