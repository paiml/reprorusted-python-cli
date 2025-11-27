.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_redis_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python redis_cli.py --mode builder

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile redis_cli.py -o redis_protocol

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f redis_protocol

io-check:
	@echo "I/O check not implemented for this example"
