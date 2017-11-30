# -*- coding: utf-8 -*-
from setuptools import setup
from setuptools import find_packages

setup(
    name='Flow Matrix Web page',
    package=["flowmatrix"],
    version='0.0.3',
    description='print collected flow matrices from influxdb',
    author='Nicolas Herbaut',
    author_email='nicolas.herbaut@univ-grenoble-alpes.fr',
    url='https://nextnet.top',
    scripts=['flow-matrix'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "chardet==3.0.4",
        "click==6.7",
        "Flask==0.12.2",
        "idna==2.6",
        "influxdb==5.0.0",
        "itsdangerous==0.24",
        "Jinja2==2.10",
        "MarkupSafe==1.0",
        "numpy",
        "pandas==0.21.0",
        "python-dateutil==2.6.1",
        "pytz==2017.3",
        "requests==2.18.4",
        "six==1.11.0",
        "urllib3==1.22",
        "Werkzeug==0.12.2"],
    packages=find_packages()
)
