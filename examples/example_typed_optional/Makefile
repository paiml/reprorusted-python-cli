.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_typed_optional_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python typed_optional_cli.py safe-div 10 3

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile typed_optional_cli.py -o typed_optional

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f typed_optional

io-check:
	@echo "I/O check not implemented for this example"
