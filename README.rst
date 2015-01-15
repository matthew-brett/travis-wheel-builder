###########################################
Repo for building Linux wheels on travis-ci
###########################################

This repo is to build Linux wheels on travis-ci, and upload them to the
scikit-learn Rackspace container, pointed to by
http://travis-wheels.scikit-image.org.

We can then use these wheels in travis-ci runs for testing other software such
as `sckit-image <https://github.com/scikit-image>`_ and `dipy
<https://github.com/nipy/dipy>`_.

At the moment the build recipes are in bash, in the file
``travis_install.py``.  If you are adding a new package you want to build, you
should add any ``apt-get`` or Python dependencies to the relevant sections in
the ``travis_install.py`` script, and modify the ``TO_BUILD`` environment
variable in ``.travis.yml``.

Contact github users @matthew-brett or @blink1073 to get access to the
repository, or submit a pull request here.
