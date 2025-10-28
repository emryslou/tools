from setuptools import setup, find_packages
from tools import __version__, __author__, __author_email__

setup(
    name='tools',
    version=__version__,
    description='Python tools collection for various tasks.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author=__author__,
    author_email=__author_email__,
    url='https://github.com/emryslou/tools',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[],
    entry_points={
        'console_scripts': [
            'tools=tools.cli:cli',
        ],
    },
)