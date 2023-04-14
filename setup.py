from setuptools import setup, find_packages

setup(
    name = 'pss_protest_578390257',
    version = '0.0.7',
    description = 'SKA PSS Product Testing Framework test libraries',
    url = 'https://gitlab.com/',
    author = 'Benjamin Shaw',
    author_email = 'ben@perfectsquares.net',
    license = 'BSD 2-clause',
    packages = find_packages(where="src"),
    package_dir = {"": "src"},
    include_package_data = True,
    scripts = ['bin/protest'],
    install_requires=['numpy',
                      'requests',
                      'pytest-mock',
                      'pytest-html',
                      'pytest-repeat',
                      'pytest-bdd',
                      'pytest'
                      ],

    classifiers=[
        'Programming Language :: Python :: 3.6',
    ],
)
