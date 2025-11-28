.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_heap_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python heap_cli.py 3 1 4 1 5 9 2 6 --mode sort

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile heap_cli.py -o heap_queue

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f heap_queue

io-check:
	@echo "I/O check not implemented for this example"
