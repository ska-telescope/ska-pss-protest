from setuptools import setup, find_packages

with open('VERSION.txt') as version_file:
        version = version_file.read()

setup(
    name = 'ska_pss_protest',
    version = version,
    description = 'SKA PSS Product Testing Framework',
    url = 'https://gitlab.com/ska-telescope/pss/ska-pss-protest',
    author = 'Benjamin Shaw, Lina Levin Preston',
    author_email = 'benjamin.shaw@manchester.ac.uk, lina.preston@manchester.ac.uk',
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
    extras_require = {
        'dev': ['black',
                'isort',
                'flake8',
                'pylint',
                'pylint-junit'
                ]
        },
    classifiers=[
        'Programming Language :: Python :: 3.6',
    ],
)
