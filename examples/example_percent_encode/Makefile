.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_urlencode_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && echo "hello world" | python urlencode_cli.py

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile urlencode_cli.py -o percent_encode

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f percent_encode

io-check:
	@echo "I/O check not implemented for this example"
