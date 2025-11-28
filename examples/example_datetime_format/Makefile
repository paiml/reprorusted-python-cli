.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_datetime_format_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python datetime_format_cli.py examples

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile datetime_format_cli.py -o datetime_format

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f datetime_format

io-check:
	@echo "I/O check not implemented for this example"
