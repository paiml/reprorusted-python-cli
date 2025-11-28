.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_settings_cli.py -v

run:
	@echo "Run with: python settings_cli.py load config.json"

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile settings_cli.py -o settings_loader

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f settings_loader

io-check:
	@echo "I/O check not implemented for this example"
