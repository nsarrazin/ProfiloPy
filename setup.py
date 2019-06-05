from setuptools import setup, find_namespace_packages, find_packages
import sys


# ver_path = convert_path('sim_common/version.py')
# with open(ver_path) as ver_file:
#     ns = {}
#     exec(ver_file.read(), ns)
#     version = ns['version']

setup(
    name='ProfiloPy',
    version='0.1.0',
    description='Laser profilometer processing',
    author='CD13',
    author_email='N.P.G.Sarrazin@student.tudelft.nl',
    url='https://github.com/nsarrazin/profilometer-analysis',

    install_requires=['numpy',
                      'numba',
                      'matplotlib',
                      'plotly'],
    # package_dir={'': 'profilopy'},
    packages=find_packages("profilopy"),
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'Development Status :: 2 - Pre-Alpha']
)