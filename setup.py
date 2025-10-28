from setuptools import setup, find_packages

setup(
    name='tools',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            'tools=tools.cli:cli',
        ],
    },
)