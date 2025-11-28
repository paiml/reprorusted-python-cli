.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_rename_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python rename_cli.py . --case lower --dry-run

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile rename_cli.py -o rename_batch

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f rename_batch

io-check:
	@echo "I/O check not implemented for this example"
