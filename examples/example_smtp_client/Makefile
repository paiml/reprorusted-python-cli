.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_smtp_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python smtp_cli.py --mode session

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile smtp_cli.py -o smtp_client

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f smtp_client

io-check:
	@echo "I/O check not implemented for this example"
