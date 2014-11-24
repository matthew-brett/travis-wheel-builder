# Travis install phase
# vim: let g:is_bash=1
PIPW="pip wheel -w $WHEELHOUSE"
PIPI="pip install -f http://travis-wheels.scikit-image.org"
PIPWI="pip install -f $WHEELHOUSE"
APT_INSTALL="sudo apt-get install"
BLAS_LAPACK_DEBS="libblas-dev liblapack-dev libatlas3gf-base"

function build_install {
    $PIPW $1
    $PIPWI $1
}

$PIPI wheel

for pkg_spec in $TO_BUILD; do
    IFS="=<>" read -ra pkg_name <<< "$pkg_spec"
    if [[ $pkg_name =~ ^(numpy|scipy)$ ]]; then
        $APT_INSTALL $BLAS_LAPACK_DEBS gfortran
        build_install cython
    fi
    if [[ $pkg_name =~ ^(scipy|matplotlib|pillow|h5py)$ ]]; then
        if [ -n "$NUMPY_VERSION" ]; then
            build_install numpy==$NUMPY_VERSION
        else
            build_install numpy
        fi
    fi
    if [[ $pkg_name == matplotlib ]]; then
        $APT_INSTALL libpng-dev libfreetype6-dev
    elif [[ $pkg_name == pillow ]]; then
        $APT_INSTALL libtiff4-dev libwebp-dev
    elif [[ $pkg_name == h5py ]]; then
        $APT_INSTALL libhdf5-serial-dev
    elif [[ $pkg_name == cvxopt ]]; then
        $APT_INSTALL $BLAS_LAPACK_DEBS
    fi
    unset pip_extra
    if [[ $pkg_name == scipy ]]; then
        # scipy needs -v flag otherwise travis times out for lack of output
        pip_extra="-v"
    fi
    $PIPW $pip_extra $pkg_spec
done
