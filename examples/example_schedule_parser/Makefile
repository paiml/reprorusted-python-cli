.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_schedule_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python schedule_cli.py "Mon-Fri 09:00-17:00" --format

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile schedule_cli.py -o schedule_parser

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f schedule_parser

io-check:
	@echo "I/O check not implemented for this example"
