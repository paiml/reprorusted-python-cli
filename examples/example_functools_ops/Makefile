.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_functools_ops_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python functools_ops_cli.py partial --add10 5 --square 4

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile functools_ops_cli.py -o functools_ops

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f functools_ops

io-check:
	@echo "I/O check not implemented for this example"
