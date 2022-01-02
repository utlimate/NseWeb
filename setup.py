from setuptools import setup
import nseapi

setup(
    name='NseWeb',
    version=nseapi.__version__,
    packages=['nseapi'],
    url='https://github.com/sachgbhatiya/NseWeb',
    license='',
    author='Sachin Bhatiya',
    author_email='sachinbhatiya68@gmail.com',
    description='For Download Open Interest Data from NSE website',
    install_requires=['pandas',
                      'numpy',
                      'requests']
)
