.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_async_queue_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python async_queue_cli.py transform 1 2 3 4 5

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile async_queue_cli.py -o async_queue

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f async_queue

io-check:
	@echo "I/O check not implemented for this example"
