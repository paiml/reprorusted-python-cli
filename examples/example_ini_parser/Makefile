.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_ini_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && echo "[section]\nkey = value" | python ini_cli.py -

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile ini_cli.py -o ini_parser

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f ini_parser

io-check:
	@echo "I/O check not implemented for this example"
