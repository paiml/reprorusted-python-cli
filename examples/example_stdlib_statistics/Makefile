.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_stats_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python stats_cli.py describe 1 2 3 4 5 6 7 8 9 10

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile stats_cli.py -o stdlib_statistics

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f stdlib_statistics

io-check:
	@echo "I/O check not implemented for this example"
