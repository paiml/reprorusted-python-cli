.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_byte_buffer_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python byte_buffer_cli.py create 1 2 3 4

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile byte_buffer_cli.py -o byte_buffer

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f byte_buffer

io-check:
	@echo "I/O check not implemented for this example"
