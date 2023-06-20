include .make/base.mk
include .make/python.mk

PYTHON_VARS_AFTER_PYTEST = -m unit

protest_update:
	pip uninstall ska-pss-protest
	pip install .[dev] --no-cache-dir
