.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_dict_comprehension_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python dict_comprehension_cli.py squares 5

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile dict_comprehension_cli.py -o dict_comprehension

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f dict_comprehension

io-check:
	@echo "I/O check not implemented for this example"
