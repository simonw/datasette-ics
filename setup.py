from setuptools import setup
import os

VERSION = "0.5.1"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="datasette-ics",
    description="Datasette plugin for outputting iCalendar files",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/simonw/datasette-ics",
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["datasette_ics"],
    entry_points={"datasette": ["ics = datasette_ics"]},
    install_requires=["datasette>=0.49", "ics==0.7"],
    extras_require={"test": ["pytest", "pytest-asyncio"]},
)
