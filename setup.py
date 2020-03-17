from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fr:
    requirements = fr.read().splitlines()

setup(
    name='DataRepository_patrons',
    version='v0.6.0',
    packages=find_packages('DataRepository_patrons'),
    url='https://github.com/ualibraries/DataRepository_patrons',
    license='MIT License',
    author='Chun Ly',
    author_email='astro.chun@gmail.com',
    description='Query EDS information to set EDS attributes specific for Figshare account management',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=requirements
)
