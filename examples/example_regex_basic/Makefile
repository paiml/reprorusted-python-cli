.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_regex_basic_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python regex_basic_cli.py find '\d+' 'abc123def456'

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile regex_basic_cli.py -o regex_basic

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f regex_basic

io-check:
	@echo "I/O check not implemented for this example"
