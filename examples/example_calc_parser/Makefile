.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_calc_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python calc_cli.py "2 + 3 * 4"

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile calc_cli.py -o calc_parser

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f calc_parser

io-check:
	@echo "I/O check not implemented for this example"
