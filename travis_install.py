import os
import re
import subprocess

# Travis install phase
WHEEL_SITE = "http://travis-wheels.scikit-image.org"
# The following line results in numpy wheels __not__ built against ATLAS
BLAS_LAPACK_DEBS = "libblas-dev liblapack-dev libatlas3gf-base"
# To build against ATLAS (and therefore have this apt-get dependency) use:
# BLAS_LAPACK_DEBS = "libatlas-base-dev"
ENV = os.environ
PYVER = ENV['TRAVIS_PYTHON_VERSION']
WHEELHOUSE = ENV['WHEELHOUSE']

PYSIDE_VERSION = ENV.get('PYSIDE_VERSION', '1.2.4')

# Packages known to need numpy
NEEDS_NUMPY = ("scipy matplotlib pillow h5py scikit-learn astropy "
               "scikit-image pandas dipy nipy statsmodels pymvpa2 "
               "PyWavelets pytables")
# Packages known to need scipy
NEEDS_SCIPY = "scikit-learn statsmodels dipy"
# Packages known to need Cython
NEEDS_CYTHON = "numpy scipy h5py"

# Arguments to pip install, wheel using Rackspace wheelhouse
WHEEL_SITE_ARGS='--timeout=60 --trusted-host {0} -f {1}'.format(
    WHEEL_SITE.replace('http://', ''), WHEEL_SITE)


def run(cmd):
    print(cmd)
    subprocess.check_call(cmd, shell=True)


def apt_install(*pkgs):
    """Install packages using apt"""
    run('sudo apt-get install -q %s' % ' '.join(pkgs))


def pipi(*args):
    """Install package from the wheel site or on PyPI"""
    run('pip install {0} {1}'.format(WHEEL_SITE_ARGS, ' '.join(args)))


def pipw(names, specs, extra_args=''):
    """Create a wheel for package(s) with `names` and specs `specs`
    """
    if not isinstance(names, (list, tuple)):
        names = [names]
    if not isinstance(specs, (list, tuple)):
        specs = [specs]
    run('pip wheel -w {wheelhouse} {all_args} '
        '--no-binary {pkg_names} {specs}'.format(
            wheelhouse=WHEELHOUSE,
            all_args='{0} {1}'.format(WHEEL_SITE_ARGS, extra_args),
            pkg_names=','.join(names),
            specs=' '.join(specs)))


def spec_to_name(pkg_spec):
    pkg_name = re.split('[\[ =<>!,]*', pkg_spec)[0]
    return pkg_name.lower()


# Install the packages we need to build wheels
if 'PRE_BUILD' in ENV:
    pipi('wheel', ENV['PRE_BUILD'])

sources = ENV.get('SOURCES', '').split()
pkg_specs = ENV['TO_BUILD'].split()
if not sources:
    sources = ['pypi'] * len(pkg_specs)

for pkg_spec, source in zip(pkg_specs, sources):
    # Get package name from package spec
    # e.g. "matplotlib" from "matplotlib==1.3.1"
    pkg_name = spec_to_name(pkg_spec)

    if pkg_name in 'numpy scipy'.split():
        apt_install(BLAS_LAPACK_DEBS, 'gfortran')

    ########################################
    # First install any package dependencies
    ########################################

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

    elif pkg_name in ('h5py', 'tables'):
        apt_install('libhdf5-serial-dev')

    elif pkg_name in 'cvxopt scikit-learn'.split():
        apt_install(BLAS_LAPACK_DEBS)

    elif pkg_name == 'simpleitk':
        apt_install('cmake')

    elif pkg_name == 'scikit-image':
        pipi('six')

    elif pkg_name == 'imread':
        apt_install('libtiff4-dev libwebp-dev libpng12-dev xcftools')

    elif pkg_name == 'pil':
        run('sudo apt-get build-dep python-imaging')
        run('sudo apt-get install python-dev')
        run('sudo ln -s /usr/lib/x86_64-linux-gnu/libfreetype.so /usr/lib/')
        run('sudo ln -s /usr/lib/x86_64-linux-gnu/libz.so /usr/lib/')
        run('sudo ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib/')

    elif pkg_name == 'pymvpa2':
        run('sudo apt-get install swig')

    elif pkg_name == 'pyside':
        apt_install('build-essential git cmake libqt4-dev libphonon-dev')
        apt_install('python2.7-dev libxml2-dev libxslt1-dev qtmobility-dev')
        pyside_root = 'PySide-{0}'.format(PYSIDE_VERSION)
        pyside_archive = pyside_root + '.tar.gz'
        run('wget https://pypi.python.org/packages/source/P/PySide/' +
            pyside_archive)
        run('tar -xvzf ' + pyside_archive)

    ##########################
    # Next build package wheel
    ##########################

    if source == 'pypi':
        source = pkg_spec

    # scipy needs -v flag otherwise travis times out for lack of output
    if pkg_name == 'scipy':
        pipw(pkg_name, source, '-v')

    elif pkg_name == 'simpleitk':
        link = 'http://sourceforge.net/projects/simpleitk/files/SimpleITK/0.8.0/Python/SimpleITK-0.8.0-cp%s-%s-linux_x86_64.whl'
        ver = PYVER.replace('.', '')
        if ver in ['26', '27']:
            link = link % (ver, 'none')
        elif ver in ['32', '33']:
            link = link % (ver, 'cp%sm' % ver)
        else:
            continue
        run('wget %s -P %s' % (link, WHEELHOUSE))

    elif pkg_name == 'pil':
        pipw(pkg_name, source,
            '--allow-external PIL --allow-unverified PIL')

    elif pkg_name == 'pyside':
        # patch for Py35 compatibility
        run("cd {0} && sed -i 's/subprocess.mswindows/False/g' popenasync.py"
            .format(pyside_root))
        run('cd {0} && python setup.py bdist_wheel --qmake=/usr/bin/qmake-qt4 '
            '-d {1}'.format(pyside_root, WHEELHOUSE))
    else:
        pipw(pkg_name, source)
