# -*- coding: utf-8 -*-
from setuptools import setup
from setuptools import find_packages

with open("requirements.txt") as requirements_file:
    install_requires = requirements_file.read().split("\n")


setup(
    name='Flow Matrix Web page',
    package=["flowmatrix"],
    version='0.0.3',
    description='print collected flow matrices from influxdb',
    author='Nicolas Herbaut',
    author_email='nicolas.herbaut@univ-grenoble-alpes.fr',
    url='https://nextnet.top',
    scripts=['bin/flow-matrix'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    packages=find_packages()
)
