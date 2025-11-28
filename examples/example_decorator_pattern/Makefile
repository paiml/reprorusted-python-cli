.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_decorator_pattern_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python decorator_pattern_cli.py timed 10 20

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile decorator_pattern_cli.py -o decorator_pattern

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f decorator_pattern

io-check:
	@echo "I/O check not implemented for this example"
