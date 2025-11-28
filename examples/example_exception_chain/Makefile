.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_exception_chain_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python exception_chain_cli.py config "host=localhost"

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile exception_chain_cli.py -o exception_chain

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f exception_chain

io-check:
	@echo "I/O check not implemented for this example"
