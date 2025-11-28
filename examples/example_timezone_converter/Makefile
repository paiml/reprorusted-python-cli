.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_tz_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python tz_cli.py now -f UTC -t PST

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile tz_cli.py -o timezone_converter

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f timezone_converter

io-check:
	@echo "I/O check not implemented for this example"
