.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_datetime_calendar_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python datetime_calendar_cli.py month 2024 6

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile datetime_calendar_cli.py -o datetime_calendar

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f datetime_calendar

io-check:
	@echo "I/O check not implemented for this example"
