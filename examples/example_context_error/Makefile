.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_context_error_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python context_error_cli.py resource test "hello world"

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile context_error_cli.py -o context_error

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f context_error

io-check:
	@echo "I/O check not implemented for this example"
