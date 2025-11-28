.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_sort_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python sort_cli.py 3 1 4 1 5 9 2 6

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile sort_cli.py -o merge_sort

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f merge_sort

io-check:
	@echo "I/O check not implemented for this example"
