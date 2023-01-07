from setuptools import setup, find_packages
import os

__version__ = '0.0.4'


def get_long_description(filename):
    root_dir = os.path.abspath(os.path.curdir)
    if root_dir.endswith('/src'):
        root_dir = root_dir.replace('/src', '')
    full_path = os.path.join(root_dir, filename)
    if not os.path.exists(full_path):
        raise ValueError(f'{filename} could not be found at {full_path}')

    with open(full_path) as f:
        description = f.read()

    return description


setup(
    name='py_ddd_framework',
    version=__version__,
    description='Python Domain-Driven Design (DDD) Framework',
    long_description=get_long_description('README.md'),
    author='Victor Klapholz',
    author_email='victor.klapholz@gmail.com',
    url='https://github.com/vklap/py_ddd_framework',
    keywords='DDD Domain Driven Design Framework',
    license='MIT',
    packages=['ddd'],
    package_dir={'': 'src'},
    install_requires=[],
    tests_require=[
        "pytest>=7.2.0",
        "pytest-asyncio>=0.20.3",
    ],
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
