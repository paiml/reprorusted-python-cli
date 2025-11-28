.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_sync_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python sync_cli.py --status . /tmp/sync_test

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile sync_cli.py -o file_sync

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f file_sync

io-check:
	@echo "I/O check not implemented for this example"
