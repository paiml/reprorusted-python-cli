.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_toml_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && echo '[server]\nport = 8080' | python toml_cli.py -

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile toml_cli.py -o toml_reader

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f toml_reader

io-check:
	@echo "I/O check not implemented for this example"
