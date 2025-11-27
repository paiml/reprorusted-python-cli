.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_nested_function_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python nested_function_cli.py stats 1 2 3 4 5

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile nested_function_cli.py -o nested_function

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f nested_function

io-check:
	@echo "I/O check not implemented for this example"
