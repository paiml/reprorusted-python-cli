.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_custom_exception_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python custom_exception_cli.py validate --username alice

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile custom_exception_cli.py -o custom_exception

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f custom_exception

io-check:
	@echo "I/O check not implemented for this example"
