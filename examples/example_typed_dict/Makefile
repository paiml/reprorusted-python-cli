.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_typed_dict_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python typed_dict_cli.py create a=1 b=2 c=3

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile typed_dict_cli.py -o typed_dict

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f typed_dict

io-check:
	@echo "I/O check not implemented for this example"
