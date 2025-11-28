.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_typed_list_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python typed_list_cli.py create 1 2 3 4 5

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile typed_list_cli.py -o typed_list

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f typed_list

io-check:
	@echo "I/O check not implemented for this example"
