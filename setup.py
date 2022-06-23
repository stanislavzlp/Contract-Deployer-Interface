from pathlib import Path

from setuptools import setup, find_packages

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='mywish_deployer',
    version='0.3.2',
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'eth-brownie==1.19.0',
    ],
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type='text/markdown'

)
