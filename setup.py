#!/usr/bin/env python

from os.path import exists
from setuptools import setup


setup(name='uncomtrader',
      version='1.0.0',
      description='UN Comtrade Data Scraper',
      url='https://github.com/moody-marlin/un_comtrader.git',
      maintainer='Chris White',
      maintainer_email='white.cdw@gmail.com',
      packages=['uncomtrader'],
      long_description=(open('README.rst').read() if exists('README.rst')
                        else ''),
      install_requires=list(open('requirements.txt').read().strip().split('\n')),
      zip_safe=False)
