include .make/base.mk
include .make/python.mk

PYTHON_VARS_AFTER_PYTEST = -m unit --ignore=src

protest_update:
	pip uninstall ska-pss-protest
	pip install .[dev] --no-cache-dir
