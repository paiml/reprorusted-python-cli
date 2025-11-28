.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_set_comprehension_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python set_comprehension_cli.py squares 1 2 3 4

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile set_comprehension_cli.py -o set_comprehension

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f set_comprehension

io-check:
	@echo "I/O check not implemented for this example"
