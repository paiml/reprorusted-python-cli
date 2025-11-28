.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_regex_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python regex_cli.py "a.*b" "axyzb"

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile regex_cli.py -o regex_matcher

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f regex_matcher

io-check:
	@echo "I/O check not implemented for this example"
