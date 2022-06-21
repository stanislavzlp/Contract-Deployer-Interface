from setuptools import setup, find_packages


setup(
    name='mywish_deployer',
    version='0.3.1',
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'eth-brownie==1.19.0',
    ],
    packages=find_packages(),
)
