.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_json_basic_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python json_basic_cli.py parse '{"name": "test", "value": 42}'

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile json_basic_cli.py -o json_basic

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f json_basic

io-check:
	@echo "I/O check not implemented for this example"
