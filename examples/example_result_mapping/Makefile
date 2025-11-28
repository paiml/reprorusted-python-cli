.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_result_mapping_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python result_mapping_cli.py parse 42

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile result_mapping_cli.py -o result_mapping

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f result_mapping

io-check:
	@echo "I/O check not implemented for this example"
