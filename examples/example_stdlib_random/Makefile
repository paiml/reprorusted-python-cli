.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_random_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python random_cli.py dice -n 3 -s 6

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile random_cli.py -o stdlib_random

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f stdlib_random

io-check:
	@echo "I/O check not implemented for this example"
