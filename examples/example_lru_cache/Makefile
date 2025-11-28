.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_cache_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python cache_cli.py put:a:1 put:b:2 get:a get:c --mode stats

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile cache_cli.py -o lru_cache

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f lru_cache

io-check:
	@echo "I/O check not implemented for this example"
