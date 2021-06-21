from setuptools import setup

setup(
    use_scm_version={"write_to": "qt_extras/_version.py"},
    setup_requires=["setuptools_scm"],
)
