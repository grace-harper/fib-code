"""A setuptools based setup module.
Run using:
    $ python -m pip install <flags> .
Most used flags:
    -e, --editable <path/url>
        Install a project in editable mode (i.e. setuptools “develop mode”)
        from a local project path or a VCS url.
    -v, --verbose
        Give more output.
"""
# pylint: disable=invalid-name

from pathlib import Path

from setuptools import find_packages, setup

here = Path(__file__).parent.absolute()  # pylint: disable=no-member

# Get the long description from the README file
with open(here / "README.md", encoding="utf-8") as f:
    long_description = f.read()

with open(here / "requirements.txt", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="fib_code",
    version="0.0.1",
    description="Fib Code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/grace-harper-ibm/fib-code",
    author="grace harper",
    license="Apache 2.0",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering",
    ],
    keywords="qiskit fibcode",
    packages=find_packages(),
    package_data={"": ["*.ui", "*.qrc", "_imgs/*.png", "_imgs/*.txt"]},
    python_requires=">=3.9",
    install_requires=requirements,
    project_urls={
        "Bug Tracker": "https://github.com/Qiskit/qiskit-metal/issues",
        "Documentation": "https://qiskit.org/documentation/metal",
        "Source Code": "https://github.com/Qiskit/qiskit-metal",
    },
)
