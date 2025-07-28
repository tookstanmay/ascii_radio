from setuptools import setup, find_packages

setup(
    name="ascii_radio",
    version="0.1.0",
    description="Terminal-based Indian radio streaming app using MPV and curses",
    author="Tanmay Sharma",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "ascii-radio = ascii_radio:main_wrapper",
        ],

    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "Operating System :: POSIX :: Linux",
    ],
)
