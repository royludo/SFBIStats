from setuptools import setup

setup(name='sfbistats',
      version='0.1',
      description='Job stats from SFBI website',
      url='https://github.com/royludo/SFBIStats',
      author='lroy',
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
