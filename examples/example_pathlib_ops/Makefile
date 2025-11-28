.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_pathlib_ops_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python pathlib_ops_cli.py ls .

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile pathlib_ops_cli.py -o pathlib_ops

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f pathlib_ops

io-check:
	@echo "I/O check not implemented for this example"
