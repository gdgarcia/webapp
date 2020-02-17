"""webapp
"""

from setuptools import setup, find_packages

__author__ = 'Glaucon Garcia'
__description__ = 'webapp'
__url__ = 'https://github.com/gdgarcia/webapp'
__copyright__ = 'Cortes Consultoria Ltda'
__title__ = 'webapp'
__keywords__ = 'webapp'
__credits__ = ['Glaucon Garcia']
__license__ = 'proprietary'
__version__ = '0.0.1'
__maintainer__ = 'Glaucon Garcia'
__email__ = 'ggarcia@cortesconsultoria.com.br'
__status__ = 'Development'

if __name__ == '__main__':

    setup(
        name=__title__,
        version=__version__,
        url=__url__,
        description=__description__,
        long_description=__description__,
        author=__author__,
        author_email=__email__,
        license=__license__,
        keywords=__keywords__,
        packages=find_packages(),
        include_package_data=True,
        install_requires=['julia',],
        classifiers=[
            'Development Status :: 1 - Development',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3',
            'Topic :: Utilities'
        ]
    )
