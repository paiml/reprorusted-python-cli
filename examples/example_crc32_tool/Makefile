.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_crc32_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && echo "hello" | python crc32_cli.py

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile crc32_cli.py -o crc32_tool

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f crc32_tool

io-check:
	@echo "I/O check not implemented for this example"
