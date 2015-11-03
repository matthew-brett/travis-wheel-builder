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
               "scikit-image pandas dipy nipy statsmodels")
# Packages known to need scipy
NEEDS_SCIPY = "scikit-learn"
# Packages known to need Cython
NEEDS_CYTHON = "numpy scipy h5py"


def run(cmd):
    print(cmd)
    subprocess.check_call(cmd, shell=True)


def apt_install(*pkgs):
    """Install packages using apt"""
    run('sudo apt-get install -q %s' % ' '.join(pkgs))


def pipi(*args):
    """Install package from the wheel site or on PyPI"""
    run('pip install --timeout=60 --trusted-host %s -f %s %s' %
        (WHEEL_SITE.replace('http://', ''), WHEEL_SITE, ' '.join(args)))


def pipw(*args):
    """Create a wheel for a package in the WHEELHOUSE"""
    run('pip wheel -w %s %s' %
        (ENV['WHEELHOUSE'], ' '.join(args)))


# Install the packages we need to build wheels
if 'PRE_BUILD' in ENV:
    pipi('wheel', ENV['PRE_BUILD'])

for pkg_spec in ENV['TO_BUILD'].split():
    # Get package name from package spec
    # e.g. "matplotlib" from "matplotlib==1.3.1"
    pkg_name = re.split('[\[ =<>!,]*', pkg_spec)[0]
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

    if pkg_name in NEEDS_CYTHON.split():
        pipi('--ignore-installed cython')

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

    elif pkg_name_lc == 'imread':
        apt_install('libtiff4-dev libwebp-dev libpng12-dev xcftools')

    elif pkg_name_lc == 'pil':
        run('sudo apt-get build-dep python-imaging')
        run('sudo apt-get install python-dev')
        run('sudo ln -s /usr/lib/x86_64-linux-gnu/libfreetype.so /usr/lib/')
        run('sudo ln -s /usr/lib/x86_64-linux-gnu/libz.so /usr/lib/')
        run('sudo ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib/')

    elif pkg_name_lc == 'pyside':
        apt_install('build-essential git cmake libqt4-dev libphonon-dev')
        apt_install('python2.7-dev libxml2-dev libxslt1-dev qtmobility-dev')
        run('wget https://pypi.python.org/packages/source/P/PySide/PySide-1.2.2.tar.gz')
        run('tar -xvzf PySide-1.2.2.tar.gz')

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

    elif pkg_name_lc == 'pil':
        pipw('--allow-external', 'PIL', '--allow-unverified', 'PIL', 'pil')

    elif pkg_name_lc == 'pyside':
        # patch for Py35 compatibility
        run("cd PySide-1.2.2 && sed -i 's/subprocess.mswindows/False/g' popenasync.py")
        run('cd PySide-1.2.2 && python setup.py bdist_wheel --qmake=/usr/bin/qmake-qt4 -d %s' % ENV['WHEELHOUSE'])
    else:
        pipw(pkg_spec)
