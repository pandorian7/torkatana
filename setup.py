from setuptools import setup

setup(
    name="TorKatana",
    version="0.1dev",
    description="Tool to split downloaded torrents into blocks and merge them back and manupilate torrents in many other ways",
    long_description=open("README.md").read(),
    url="https://github.com/pandorian7/torkarana",
    author="Yasith Piyarathne",
    author_email="yasithpiyarathne@gmail.com",
    packages=['torkatana'],
    requires=['torrent_parser']
)