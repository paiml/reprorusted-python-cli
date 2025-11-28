.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_msgpack_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && echo '{"hello": "world"}' | python msgpack_cli.py --size -

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile msgpack_cli.py -o msgpack_lite

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f msgpack_lite

io-check:
	@echo "I/O check not implemented for this example"
