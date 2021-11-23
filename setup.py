import pathlib

import setuptools

setuptools.setup(
    name='argparse-subdec',
    version='0.1.0',
    long_description=(pathlib.Path(__file__).parent / 'README.rst').read_text(),
    long_description_content_type='text/x-rst',
    url='https://github.com/guludo/python-argparse-subdec',
    packages=['argparse_subdec'],
    extras_require={
        'tests': [
            'pytest~=6.2',
            'coverage~=5.5',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python :: 3',
    ],
)
