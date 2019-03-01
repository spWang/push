#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='git-push',
    version='1.0.0',
    description=(
        'git push helper'
    ),
    long_description=open('README.md').read(),
    author='王帅朋',
    author_email='wsp810@163.com',
    license='MIT',
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/spWang/push',
    install_requires=[
        'python-gitlab>=1.7.0',
        'xpinyin>=0.5.6'
    ]
)