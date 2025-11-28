.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_try_except_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python try_except_cli.py divide 10 2

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile try_except_cli.py -o try_except

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f try_except

io-check:
	@echo "I/O check not implemented for this example"
