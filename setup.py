from setuptools import setup
import scrapper

setup(
    name='NseWeb',
    version=scrapper.__version__,
    packages=['scrapper'],
    url='https://github.com/sachgbhatiya/NseWeb',
    license='',
    author='Sachin Bhatiya',
    author_email='sachinbhatiya68@gmail.com',
    description='For Download Open Interest Data from NSE website',
    install_requires=['pandas',
                      'numpy',
                      'aiohttp[speedups]']
)
