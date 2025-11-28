.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_datetime_delta_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python datetime_delta_cli.py range

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile datetime_delta_cli.py -o datetime_delta

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f datetime_delta

io-check:
	@echo "I/O check not implemented for this example"
