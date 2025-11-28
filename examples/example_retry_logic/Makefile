.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_retry_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python retry_cli.py --preview --attempts 5

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile retry_cli.py -o retry_logic

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f retry_logic

io-check:
	@echo "I/O check not implemented for this example"
