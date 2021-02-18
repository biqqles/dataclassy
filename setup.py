from setuptools import setup

setup(
    name='dataclassy',
    version='0.7.2',

    author='biqqles',
    author_email='biqqles@protonmail.com',
    url='https://github.com/biqqles/dataclassy',

    description='A fast and flexible reimplementation of data classes',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',

    packages=['dataclassy'],
    package_data={
        'dataclassy': ['py.typed'],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    python_requires='>=3.6',
)
