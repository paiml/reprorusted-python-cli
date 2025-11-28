.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_schema_cli.py -v

run:
	@echo "Run with: python schema_cli.py validate data.json --schema schema.json"

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile schema_cli.py -o schema_checker

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f schema_checker

io-check:
	@echo "I/O check not implemented for this example"
