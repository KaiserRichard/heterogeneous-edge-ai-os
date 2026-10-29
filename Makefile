# Host verification needs a C compiler, GNU make and Python 3.
PYTHON ?= python3
export PYTHONDONTWRITEBYTECODE := 1

.PHONY: test firmware clean
test:
	$(MAKE) -C protocol test
	$(MAKE) -C stm32 test
	$(MAKE) -C linux all test
	$(PYTHON) -m unittest discover -s scripts/stm32/tests -v
	$(PYTHON) -m unittest discover -s analysis/tests -v
	$(PYTHON) -m unittest discover -s tools/la/tests -v
	$(PYTHON) -m unittest discover -s linux/inference/tests -v

firmware:
	$(MAKE) -C stm32 firmware

clean:
	$(MAKE) -C protocol clean
	$(MAKE) -C stm32 clean
	$(MAKE) -C linux clean
	$(MAKE) -C stm32/firmware clean
	find analysis linux/inference linux/tests tools/la tools/experiments -type d -name __pycache__ -prune -exec rm -rf {} +
