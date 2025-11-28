.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_string_format_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python string_format_cli.py format "Hello, {}!" World

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile string_format_cli.py -o string_format

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f string_format

io-check:
	@echo "I/O check not implemented for this example"
