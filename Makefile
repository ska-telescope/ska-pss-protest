include .make/base.mk
include .make/python.mk

PYTHON_VARS_AFTER_PYTEST = -m unit --ignore=src --cov-config=.coveragerc
PYTHON_SWITCHES_FOR_PYLINT = --disable=R0801,C0301,R0904,C0200,R1732,W1514,R0913,R0903,C0209,W1202,R0902,R0914,R0401
PYTHON_SWITCHES_FOR_FLAKE8 = --ignore=E501,W503
