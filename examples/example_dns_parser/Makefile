.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_dns_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python dns_cli.py --mode query --domain example.com --type A

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile dns_cli.py -o dns_parser

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f dns_parser

io-check:
	@echo "I/O check not implemented for this example"
