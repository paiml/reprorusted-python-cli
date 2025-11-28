.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_tsdiff_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python tsdiff_cli.py "2023-01-01" "2024-01-01"

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile tsdiff_cli.py -o timestamp_diff

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f timestamp_diff

io-check:
	@echo "I/O check not implemented for this example"
