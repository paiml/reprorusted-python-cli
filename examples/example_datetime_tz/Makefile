.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_datetime_tz_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python datetime_tz_cli.py world

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile datetime_tz_cli.py -o datetime_tz

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f datetime_tz

io-check:
	@echo "I/O check not implemented for this example"
