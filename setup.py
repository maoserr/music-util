"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name="music-util",
    version="1.0.0",
    description="Collection of utilities for musicians",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/maoserr/epublifier/music-util",
    author="Maoserr",
    author_email="maoserr@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Musicians",
        "Topic :: Audio :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="music, utility",
    package_dir={"": "music_util"},  # Optional
    packages=find_packages(where="src"),  # Required
    python_requires=">=3.7, <4",
    # This field lists other packages that your project depends on to run.
    # Any package you put here will be installed by pip when your project is
    # installed, so they must be valid existing projects.
    #
    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/discussions/install-requires-vs-requirements/
    install_requires=["demucs>=4.0.1", "sv-ttk>=2.5.5"],  # Optional
    # List additional groups of dependencies here (e.g. development
    # dependencies). Users will be able to install these using the "extras"
    # syntax, for example:
    #
    #   $ pip install sampleproject[dev]
    #
    # Similar to `install_requires` above, these must be valid existing
    # projects.
    extras_require={  # Optional
        "spleeter": ["spleeter>=2.3.0"],
    },
    # If there are data files included in your packages that need to be
    # installed, specify them here.
    package_data={  # Optional
        "sample": ["package_data.dat"],
    },
    # Entry points. The following would provide a command called `sample` which
    # executes the function `main` from this package when invoked:
    entry_points={  # Optional
        "console_scripts": [
            "musutil=main:main",
        ],
    },
    project_urls={  # Optional
        "Bug Reports": "https://github.com/maoserr/epublifier/music-util/issues",
        "Source": "https://github.com/maoserr/epublifier/music-util/",
    },
)
