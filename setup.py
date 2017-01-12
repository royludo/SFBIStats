try:
    from setuptools import setup, find_packages
except ImportError:
    raise ImportError("Sfbistats could not be installed, probably"
                      " because setuptools is not installed on this"
                      " computer.")

setup(name='sfbistats',
      version='1.0',
      description='Data and charts related to the french bioinformatics job market.',
      url='https://github.com/royludo/SFBIStats',
      author='Ludovic Roy',
      author_email='royludo4@hotmail.com',
      license='DO WHAT THE FUCK YOU WANT',
      packages=find_packages(exclude='examples'),
      install_requires=['numpy',
                        'pymongo',
                        'geopy'],
      extras_require = {
          'all': ['scrapy'],
      },
      package_data={'': ['utils/*.txt',
                         'utils/*.csv']},
      zip_safe=False)
