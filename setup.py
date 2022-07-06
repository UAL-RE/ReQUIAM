from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fr:
    requirements = fr.read().splitlines()

setup(
    name='requiam',
    version='v1.1.0',
    packages=['requiam'],
    url='https://github.com/UAL-RE/ReQUIAM',
    license='MIT License',
    author='Yan Han',
    author_email='astro.chun@gmail.com',
    description='Query EDS information to set EDS attributes specific for Figshare account management',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=requirements
)
