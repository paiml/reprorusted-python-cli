.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_async_context_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python async_context_cli.py resource myresource

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile async_context_cli.py -o async_context

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f async_context

io-check:
	@echo "I/O check not implemented for this example"
