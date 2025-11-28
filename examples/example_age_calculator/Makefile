.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_age_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python age_cli.py 1990-01-15

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile age_cli.py -o age_calculator

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f age_calculator

io-check:
	@echo "I/O check not implemented for this example"
