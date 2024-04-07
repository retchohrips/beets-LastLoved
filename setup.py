from setuptools import setup

setup(
    name="beets-lastloved",
    version="0.1.2",
    description="Plugin for beets (https://beets.io) to import loved track values from last.fm",
    long_description=open("README.md").read(),
    author="retchohrips",
    url="https://github.com/retchohrips/beets-lastloved",
    platforms="ALL",
    packages=["beetsplug"],
    install_requires=["beets", "pylast"],
    classifiers=[
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Sound/Audio :: Players :: MP3",
        "Environment :: Console",
        "Programming Language :: Python :: 3",
    ],
)
