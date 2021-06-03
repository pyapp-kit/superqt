from setuptools import setup

setup(
    use_scm_version={"write_to": "qwidgets/_version.py"},
    setup_requires=["setuptools_scm"],
)
