.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_struct_pack_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python struct_pack_cli.py pack int 12345678

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile struct_pack_cli.py -o struct_pack

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f struct_pack

io-check:
	@echo "I/O check not implemented for this example"
