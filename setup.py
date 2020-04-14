from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fr:
    requirements = fr.read().splitlines()

setup(
    name='ReQUIAM',
    version='v0.8.3',
    packages=find_packages('ReQUIAM'),
    url='https://github.com/ualibraries/ReQUIAM',
    license='MIT License',
    author='Chun Ly',
    author_email='astro.chun@gmail.com',
    description='Query EDS information to set EDS attributes specific for Figshare account management',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=requirements
)
