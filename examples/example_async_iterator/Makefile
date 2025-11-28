.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_async_iterator_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python async_iterator_cli.py fibonacci 10

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile async_iterator_cli.py -o async_iterator

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f async_iterator

io-check:
	@echo "I/O check not implemented for this example"
