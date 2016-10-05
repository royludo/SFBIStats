from setuptools import setup

setup(name='sfbistats',
      version='1.0',
      description='Data and charts related to the french bioinformatics job market.',
      url='https://github.com/royludo/SFBIStats',
      author='Ludovic Roy',
      author_email='royludo4@hotmail.com',
      license='DO WHAT THE FUCK YOU WANT',
      packages=['sfbistats',
                'sfbistats.utils',
                'sfbistats.loader'],
      install_requires=['numpy',
                        'pymongo',
                        'geopy'],
      package_data={'': ['utils/*.txt',
                         'utils/*.csv']},
      zip_safe=False)
