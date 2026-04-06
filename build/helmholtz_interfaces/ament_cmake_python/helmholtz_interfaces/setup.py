from setuptools import find_packages
from setuptools import setup

setup(
    name='helmholtz_interfaces',
    version='0.0.0',
    packages=find_packages(
        include=('helmholtz_interfaces', 'helmholtz_interfaces.*')),
)
