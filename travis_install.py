import os
import re
import subprocess

# Travis install phase
WHEEL_SITE = "http://travis-wheels.scikit-image.org"
BLAS_LAPACK_DEBS = "libblas-dev liblapack-dev libatlas3gf-base"
ENV = os.environ
PYVER = ENV['TRAVIS_PYTHON_VERSION']

# Packages known to need numpy
NEEDS_NUMPY = ("scipy matplotlib pillow h5py scikit-learn astropy"
               "scikit-image")
# Packages known to need scipy
NEEDS_SCIPY = "scikit-learn"


def run(cmd):
    print(cmd)
    subprocess.check_call(cmd, shell=True)


def apt_install(*pkgs):
    """Install packages using apt"""
    run('sudo apt-get install %s' % ' '.join(pkgs))


def pipi(*args):
    """Install package from the wheel site or on PyPI"""
    run('pip install -timeout=60 -f %s %s' %
        (WHEEL_SITE, ' '.join(args)))


def pipw(*args):
    """Create a wheel for a package in the WHEELHOUSE"""
    run('pip wheel -w %s %s' %
        (ENV['WHEELHOUSE'], ' '.join(args)))


# Install the packages we need to build wheels
pipi('wheel', ENV['PRE_BUILD'])

for pkg_spec in ENV['TO_BUILD'].split():
    # Get package name from package spec
    # e.g. "matplotlib" from "matplotlib==1.3.1"
    pkg_name = re.split('\W', pkg_spec)[0]
    pkg_name_lc = pkg_name.lower()

    if pkg_name in 'numpy scipy'.split():
        apt_install(BLAS_LAPACK_DEBS, 'gfortran')

    # Some packages need numpy.
    # NUMPY_VERSION specifies a specific version
    if pkg_name in NEEDS_NUMPY.split():
        if "NUMPY_VERSION" in ENV:
            pipi('numpy==%s' % ENV['NUMPY_VERSION'])
        else:
            pipi('numpy')

    if pkg_name in NEEDS_SCIPY.split():
        pipi('scipy')

    if pkg_name == 'matplotlib':
        apt_install('libpng-dev libfreetype6-dev')
        # Python 3.2 only compiles up to 1.3.1
        if pkg_name == pkg_spec and PYVER == "3.2":
            pkg_spec = "matplotlib==1.3.1"

    elif pkg_name in 'pillow tifffile'.split():
        apt_install('libtiff4-dev libwebp-dev')

    elif pkg_name == 'h5py':
        apt_install('libhdf5-serial-dev')

    elif pkg_name in 'cvxopt scikit-learn'.split():
        apt_install(BLAS_LAPACK_DEBS)

    elif pkg_name_lc == 'simpleitk':
        apt_install('cmake')

    elif pkg_name_lc == 'scikit-image':
        pipi('six')

    # scipy needs -v flag otherwise travis times out for lack of output
    if pkg_name_lc == 'scipy':
        pipw('-v', pkg_spec)

    elif pkg_name_lc == 'simpleitk':
        link = 'http://sourceforge.net/projects/simpleitk/files/SimpleITK/0.8.0/Python/SimpleITK-0.8.0-cp%s-%s-linux_x86_64.whl'
        ver = PYVER.replace('.', '')
        if ver in ['26', '27']:
            link = link % (ver, 'none')
        elif ver in ['32', '33']:
            link = link % (ver, 'cp%sm' % ver)
        else:
            continue
        run('wget %s -P %s' % (link, ENV['WHEELHOUSE']))

    else:
        pipw(pkg_spec)
