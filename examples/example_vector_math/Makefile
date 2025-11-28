.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_vector_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python vector_cli.py --mode demo

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile vector_cli.py -o vector_math

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f vector_math

io-check:
	@echo "I/O check not implemented for this example"
