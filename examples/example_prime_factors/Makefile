.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_prime_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python prime_cli.py 360 --mode factor

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile prime_cli.py -o prime_factors

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f prime_factors

io-check:
	@echo "I/O check not implemented for this example"
