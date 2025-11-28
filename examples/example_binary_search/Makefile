.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_search_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python search_cli.py 5 1 3 5 7 9

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile search_cli.py -o binary_search

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f binary_search

io-check:
	@echo "I/O check not implemented for this example"
