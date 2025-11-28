.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_timeout_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python timeout_cli.py 30s --check

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile timeout_cli.py -o timeout_handler

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f timeout_handler

io-check:
	@echo "I/O check not implemented for this example"
