.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_batch_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python batch_cli.py -n 50 -b 10 --progress

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile batch_cli.py -o batch_processor

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f batch_processor

io-check:
	@echo "I/O check not implemented for this example"
