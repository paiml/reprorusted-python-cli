.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_bitwise_ops_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python bitwise_ops_cli.py binary 255 --bits 8

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile bitwise_ops_cli.py -o bitwise_ops

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f bitwise_ops

io-check:
	@echo "I/O check not implemented for this example"
