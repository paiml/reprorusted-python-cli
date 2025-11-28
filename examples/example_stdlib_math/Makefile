.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_math_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python math_cli.py sqrt 16

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile math_cli.py -o stdlib_math

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f stdlib_math

io-check:
	@echo "I/O check not implemented for this example"
