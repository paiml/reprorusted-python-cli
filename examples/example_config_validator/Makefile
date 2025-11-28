.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_config_cli.py -v

run:
	@echo "Run with: python config_cli.py validate config.json --schema schema.json"

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile config_cli.py -o config_validator

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f config_validator

io-check:
	@echo "I/O check not implemented for this example"
