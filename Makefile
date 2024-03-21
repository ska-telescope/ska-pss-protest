include .make/base.mk
include .make/python.mk

PYTHON_VARS_AFTER_PYTEST = -m unit --ignore=src
PYTHON_SWITCHES_FOR_PYLINT = --disable=R0801,C0301,R0904,C0200,R1732,W1514 --exit-zero
PYTHON_SWITCHES_FOR_FLAKE8 = --ignore=E501,W503
