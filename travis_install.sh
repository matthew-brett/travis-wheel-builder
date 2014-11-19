# Travis install phase
PIPW="pip wheel -w $WHEELHOUSE"
PIPI="pip install wheel -f http://travis-wheels.scikit-image.org"


function build_cython {
    $PIPW cython
    pip install -f $WHEELHOUSE cython
}

function build_numpy {
    sudo apt-get install libblas-dev liblapack-dev libatlas3gf-base gfortran
    $PIPI cython
    $PIPW numpy==$NUMPY_VERSION
    pip install -f $WHEELHOUSE numpy==$NUMPY_VERSION
}

function build_matplotlib {
    sudo apt-get install libpng-dev libfreetype6-dev
    $PIPI numpy
    if [[ $TRAVIS_PYTHON_VERSION == 3.2 ]]; then
        $PIPW matplotlib==1.3.1
    else
        $PIPW matplotlib
    fi
}

function build_scipy {
    sudo apt-get install libblas-dev liblapack-dev libatlas3gf-base gfortran
    $PIPI cython numpy
    # scipy needs -v flag otherwise travis times out for lack of output
    $PIPW -v scipy
}

function build_pillow {
    sudo apt-get install libtiff4-dev libwebp-dev
    $PIPW pillow
}

function build_networkx {
    $PIPW networkx
}

function build_tifffile {
    sudo apt-get install libtiff4-dev libwebp-dev
    $PIPW tifffile
}

function build_h5py {
    sudo apt-get install libhdf5-serial-dev
    $PIPI cython numpy
    $PIPW h5py
}

if [[ $TO_BUILD == *cython* ]]; then
    build_cython
fi
if [[ $TO_BUILD == *numpy* ]]; then
    build_numpy
fi
if [[ $TO_BUILD == *scipy* ]]; then
    build_scipy
fi
if [[ $TO_BUILD == *matplotlib* ]]; then
    build_matplotlib
fi
if [[ $TO_BUILD == *pillow* ]]; then
    build_pillow
fi
if [[ $TO_BUILD == *networkx* ]]; then
    build_networkx
fi
if [[ $TO_BUILD == *tifffile* ]]; then
    build_tifffile
fi
if [[ $TO_BUILD == *h5py* ]]; then
    build_h5py
fi
