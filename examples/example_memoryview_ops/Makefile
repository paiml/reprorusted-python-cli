.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_memoryview_ops_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python memoryview_ops_cli.py create 8 --fill 255

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile memoryview_ops_cli.py -o memoryview_ops

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f memoryview_ops

io-check:
	@echo "I/O check not implemented for this example"
