from setuptools import setup

setup(
    name='dataclassy',
    version='0.5',

    author='biqqles',
    author_email='biqqles@protonmail.com',
    url='https://github.com/biqqles/dataclassy',

    description='A reimplementation of data classes in Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',

    packages=['dataclassy'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
    ],
    python_requires='>=3.6',
)
