.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_datetime_basic_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python datetime_basic_cli.py now

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile datetime_basic_cli.py -o datetime_basic

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f datetime_basic

io-check:
	@echo "I/O check not implemented for this example"
