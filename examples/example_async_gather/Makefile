.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_async_gather_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python async_gather_cli.py gather 1 2 3 4 5

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile async_gather_cli.py -o async_gather

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f async_gather

io-check:
	@echo "I/O check not implemented for this example"
