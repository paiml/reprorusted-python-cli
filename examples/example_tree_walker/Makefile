.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_tree_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python tree_cli.py .

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile tree_cli.py -o tree_walker

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f tree_walker

io-check:
	@echo "I/O check not implemented for this example"
