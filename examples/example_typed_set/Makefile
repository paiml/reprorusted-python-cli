.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_typed_set_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python typed_set_cli.py create 1 2 3 2 1

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile typed_set_cli.py -o typed_set

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f typed_set

io-check:
	@echo "I/O check not implemented for this example"
