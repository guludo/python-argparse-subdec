import setuptools

setuptools.setup(
    name='argparse-subdec',
    version='0.0.0',
    packages=['argparse_subdec'],
    extras_require={
        'tests': [
            'pytest~=6.2',
            'coverage~=5.5',
        ],
    },
)
