##########
Change Log
##########

All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.


0.4.2
*****
* Set the default output of ``AbstractFileContainer.write()`` to ``sys.stdout``.
* Cleaned up ``tests_require`` in ``setup.py``.
* Added the ``get_func_name()`` function.
* Added the ``module`` argument to ``issubclass_factory()``, ``isinstance_factory()``
  and ``import_factory()``.
* ``PartialPrepend`` and ``SetAttr`` are now in their own (private) modules.
  Note that they still should be imported from (preferably) ``nanoutils`` or
  otherwise ``nanoutils.utils.
* Run tests on the ``docs/`` directory.
* Updated annotations and documentation.


0.4.1
*****
* Minor documentation fixes.
* Added the ``ignore_if()`` decorator.


0.4.0
*****
* Added the ``AbstractFileContainer`` class and ``file_to_context()`` function.
* Marked all internally used type annotations are private.
* Added `contextlib2 <https://github.com/jazzband/contextlib2>`_ as a dependency for Python 3.6.


0.3.3
*****
* Added ``PathType``, an annotation for `path-like <https://docs.python.org/3/glossary.html#term-path-like-object>`_ objects.
* Added the ``copy`` argument to ``as_nd_array()``.


0.3.2
*****
* Fixed a bug with ``split_dict()``.


0.3.1
*****
* Added the ``disgard_keys`` argument to ``split_dict()``.


0.3.0
*****
* Added the ``SetAttr`` context manager.
* Updated the development status from alpha to beta.


0.2.0
*****
* Added new NumPy-specific functions: ``as_nd_array()``, ``array_combinations()`` & ``fill_diagonal_blocks()``.
* Expanded the ``typing_utils`` module with a number of, previously missing, objects.
* Added the ``EMPTY_CONTAINER`` constaint.
* Added the  ``VersionInfo`` namedtuple and the ``raise_if()`` & ``split_dict()`` functions.
* Added the ``version_info`` attribute to the package.


0.1.1
*****
* Updated the badges.
* Added a GitHub Actions workflow for automatic PyPi publishing.


0.1.0
*****
* First release.
* Introduced of four new modules: ``empty``, ``schema``,
  ``typing_utils`` and ``utils``.


[Unreleased]
************
* Empty Python project directory structure.
