.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_tuple_unpack_comp_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python tuple_unpack_comp_cli.py enumerate a b c

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile tuple_unpack_comp_cli.py -o tuple_unpack_comp

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f tuple_unpack_comp

io-check:
	@echo "I/O check not implemented for this example"
