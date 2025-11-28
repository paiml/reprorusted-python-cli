.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_hexdump_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && echo "Hello World" | python hexdump_cli.py

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile hexdump_cli.py -o hex_dump

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f hex_dump

io-check:
	@echo "I/O check not implemented for this example"
