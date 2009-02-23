from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='reliefcnc',
      version=version,
      description="motorized shooting for relief.fr",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='cnc usb python 3D relief',
      author='Christophe Combelles',
      author_email='ccomb@gorfou.fr',
      url='',
      license='proprietary',
      packages=find_packages(),
      #packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'setuptools',
          'pycnic',
      ],
      entry_points="""
      [console_scripts]
      shoot = reliefcnc.main:main
      """,
      )
