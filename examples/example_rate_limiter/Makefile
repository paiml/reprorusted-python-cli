.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_ratelimit_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python ratelimit_cli.py --check

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile ratelimit_cli.py -o rate_limiter

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f rate_limiter ratelimit.json

io-check:
	@echo "I/O check not implemented for this example"
