.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_expr_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python expr_cli.py "2 + 3 * 4"

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile expr_cli.py -o expression_eval

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f expression_eval

io-check:
	@echo "I/O check not implemented for this example"
