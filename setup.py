from setuptools import setup

setup(
    use_scm_version={"write_to": "superqt/_version.py"},
    setup_requires=["setuptools_scm"],
)
