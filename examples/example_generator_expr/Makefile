.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_generator_expr_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python generator_expr_cli.py squares 5

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile generator_expr_cli.py -o generator_expr

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f generator_expr

io-check:
	@echo "I/O check not implemented for this example"
