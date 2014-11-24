# Travis install phase
# vim: let g:is_bash=1
PIPW="pip wheel -w $WHEELHOUSE"
PIPI="pip install -f http://travis-wheels.scikit-image.org"
PIPWI="pip install -f $WHEELHOUSE"
APT_INSTALL="sudo apt-get install"
BLAS_LAPACK_DEBS="libblas-dev liblapack-dev libatlas3gf-base"
PYVER=$TRAVIS_PYTHON_VERSION

$PIPI wheel

for pkg_spec in $TO_BUILD; do
    IFS="=<>" read -ra pkg_name <<< "$pkg_spec"
    if [[ $pkg_name =~ ^(numpy|scipy)$ ]]; then
        $APT_INSTALL $BLAS_LAPACK_DEBS gfortran
    fi
    if [[ $pkg_name =~ ^(scipy|matplotlib|pillow|h5py)$ ]]; then
        if [ -n "$NUMPY_VERSION" ]; then
            $PIPI numpy==$NUMPY_VERSION
        else
            $PIPI numpy
        fi
    fi
    if [[ $pkg_name == matplotlib ]]; then
        $APT_INSTALL libpng-dev libfreetype6-dev
        # Python 3.2 only compiles up to 1.3.1
        if [ "$pkg_name" -eq "$pkg_spec" -a "$PYVER" -eq "3.2" ]; then
            $pkg_spec="matplotlib==1.3.1"
        fi
    elif [[ $pkg_name =~ ^(pillow|tifffile)$ ]]; then
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
