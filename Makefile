PYTHON ?= python3

.PHONY: lint validate-schema validate-config run-phase run-01 run-02 run-03 run-04 run-05 run-06 pipeline

lint:
	$(PYTHON) -m ruff check scripts

validate-schema:
	$(PYTHON) scripts/validate_config.py

validate-config: validate-schema

run-phase:
	$(PYTHON) scripts/run_phase.py $(PHASE)

run-01:
	$(PYTHON) scripts/run_phase.py 1

run-02:
	$(PYTHON) scripts/run_phase.py 2

run-03:
	$(PYTHON) scripts/run_phase.py 3

run-04:
	$(PYTHON) scripts/run_phase.py 4

run-05:
	$(PYTHON) scripts/run_phase.py 5

run-06:
	$(PYTHON) scripts/run_phase.py 6

pipeline: run-01 run-02 run-03 run-04 run-05 run-06
