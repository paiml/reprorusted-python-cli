.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_poly_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python poly_cli.py --mode demo

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile poly_cli.py -o polynomial

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f polynomial

io-check:
	@echo "I/O check not implemented for this example"
