from distutils.core import setup

VERSION = __import__("redirector").__version__

setup(
        name='django-redirector',
        packages=['redirector'],
        version=VERSION,
        description='Advanced redirect management for Django applications.',
        author='Shayne Macaulay',
        author_email='shayne@nomad.ca',
        url='https://nomad.ca',
        download_url="https://code.nomaddev.ca/works/django-redirector/tarball/{0}".format(VERSION),
        keywords=['django', 'redirector'],
        classifiers=[],
        install_requires=[
                    'django>=1.7'
                ]
)
