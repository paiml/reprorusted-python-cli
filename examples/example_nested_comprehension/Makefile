.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_nested_comprehension_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python nested_comprehension_cli.py flatten --matrix "[[1,2],[3,4]]"

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile nested_comprehension_cli.py -o nested_comprehension

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f nested_comprehension

io-check:
	@echo "I/O check not implemented for this example"
