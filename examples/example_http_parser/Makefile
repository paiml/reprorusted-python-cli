.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_http_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python http_cli.py --mode url --url "https://example.com:8080/path?key=value"

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile http_cli.py -o http_parser

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f http_parser

io-check:
	@echo "I/O check not implemented for this example"
