.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_csv_dialect_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && echo "a,b,c" | python csv_dialect_cli.py -

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile csv_dialect_cli.py -o csv_dialect

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f csv_dialect

io-check:
	@echo "I/O check not implemented for this example"
