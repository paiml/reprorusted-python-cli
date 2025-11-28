.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_matrix_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python matrix_cli.py --mode demo

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile matrix_cli.py -o matrix_ops

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f matrix_ops

io-check:
	@echo "I/O check not implemented for this example"
