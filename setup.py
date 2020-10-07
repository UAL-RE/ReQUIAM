from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fr:
    requirements = fr.read().splitlines()

setup(
    name='requiam',
    version='v0.13.0',
    packages=find_packages('requiam'),
    url='https://github.com/ualibraries/ReQUIAM',
    license='MIT License',
    author='Chun Ly',
    author_email='astro.chun@gmail.com',
    description='Query EDS information to set EDS attributes specific for Figshare account management',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=requirements
)
