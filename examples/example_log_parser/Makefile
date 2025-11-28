.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_log_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && echo '192.168.1.1 - - [10/Oct/2023:13:55:36 -0700] "GET /index.html HTTP/1.1" 200 2326 "-" "-"' | python log_cli.py -

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile log_cli.py -o log_parser

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f log_parser

io-check:
	@echo "I/O check not implemented for this example"
