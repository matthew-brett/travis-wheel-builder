# Travis install phase
PIPW="pip wheel -w $WHEELHOUSE"
PIPI="pip install --timeout=60 -f http://travis-wheels.scikit-image.org"
PIPWI="pip install -f $WHEELHOUSE"
APT_INSTALL="sudo apt-get install"
BLAS_LAPACK_DEBS="libblas-dev liblapack-dev libatlas3gf-base"
PYVER=$TRAVIS_PYTHON_VERSION
# Packages known to need numpy
NEEDS_NUMPY="scipy matplotlib pillow h5py scikit-learn"
# Packages known to need scipy
NEEDS_SCIPY="scikit-learn"

# Install packages we need to build wheels
$PIPI wheel $PRE_BUILD

name_in() {
    local target=$1
    shift
    for element in $@; do
        [[ $element == $target ]] && return 0
    done
    return 1
}

for pkg_spec in $TO_BUILD; do
    # Get package name from package spec
    # e.g. "matplotlib" from "matplotlib==1.3.1"
    IFS="=<>" read -ra pkg_name <<< "$pkg_spec"
    if name_in $pkg_name numpy scipy; then
        $APT_INSTALL $BLAS_LAPACK_DEBS gfortran
    fi
    # Some packages need numpy.
    # NUMPY_VERSION specifies a specific version
    if name_in $pkg_name $NEEDS_NUMPY; then
        if [ -n "$NUMPY_VERSION" ]; then
            $PIPI numpy==$NUMPY_VERSION
        else
            $PIPI numpy
        fi
    fi
    if name_in $pkg_name $NEEDS_SCIPY; then
        $PIPI scipy
    fi
    if [[ $pkg_name == matplotlib ]]; then
        $APT_INSTALL libpng-dev libfreetype6-dev
        # Python 3.2 only compiles up to 1.3.1
        if [ "$pkg_name" == "$pkg_spec" -a "$PYVER" == "3.2" ]; then
            pkg_spec="matplotlib==1.3.1"
        fi
    elif name_in $pkg_name pillow tifffile; then
        $APT_INSTALL libtiff4-dev libwebp-dev
    elif [[ $pkg_name == h5py ]]; then
        $APT_INSTALL libhdf5-serial-dev
    elif name_in $pkg_name cvxopt scikit-learn; then
        $APT_INSTALL $BLAS_LAPACK_DEBS
    fi
    # scipy needs -v flag otherwise travis times out for lack of output
    [[ $pkg_name == scipy ]] && pip_extra='-v' || pip_extra=''
    $PIPW $pip_extra $pkg_spec
done
