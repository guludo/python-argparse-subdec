import pathlib

import setuptools

extra_dependencies = {
    'pytest~=6.2': ['dev', 'tests'],
    'coverage~=5.5': ['dev', 'tests'],
    'mypy>=0.910<1': ['dev'],
}
extras_require = {'all': []}
for dep, topics in extra_dependencies.items():
    extras_require['all'].append(dep)
    for topic in topics:
        extras_require.setdefault(topic, [])
        extras_require[topic].append(dep)


setuptools.setup(
    name='argparse-subdec',
    version='0.2.1',
    long_description=(pathlib.Path(__file__).parent / 'README.rst').read_text(),
    long_description_content_type='text/x-rst',
    url='https://github.com/guludo/python-argparse-subdec',
    packages=['argparse_subdec'],
    package_data={
        'argparse_subdec': ['py.typed'],
    },
    extras_require=extras_require,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python :: 3',
    ],
)
