#!/usr/bin/env python3

from setuptools import setup, find_packages

README = open('README.md').readlines()

setup(
    name='django-msgpackfield',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description=README[2].rstrip('\n'),
    long_description=''.join(README),
    url='https://github.com/vakorol/django-msgpackfield',
    author='Vasili Korol',
    author_email='vakorol@mail.ru',
    install_requires=(
        'django',
        'msgpack',
        'json',
    ),
    classifiers=[
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: MIT License',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Development Status :: 4 - Beta',
    ],
)
