.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_dedup_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python dedup_cli.py . --summary

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile dedup_cli.py -o dedup_finder

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f dedup_finder

io-check:
	@echo "I/O check not implemented for this example"
