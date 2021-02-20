from setuptools import setup

setup(
    name='NseWeb',
    version='0.0.2',
    packages=['nseapi'],
    url='https://github.com/sachgbhatiya/NseWeb',
    license='',
    author='Sachin',
    author_email='sachingbhatiya@gmail.com',
    description='For Download Open Interest Data from NSE website',
    install_requires=['pandas',
                      'numpy',
                      'requests']
)
