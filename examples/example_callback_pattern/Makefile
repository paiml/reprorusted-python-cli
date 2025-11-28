.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_callback_pattern_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python callback_pattern_cli.py events

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile callback_pattern_cli.py -o callback_pattern

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f callback_pattern

io-check:
	@echo "I/O check not implemented for this example"
