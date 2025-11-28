.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_csv_basic_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python csv_basic_cli.py parse "a,b,c\n1,2,3"

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile csv_basic_cli.py -o csv_basic

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f csv_basic

io-check:
	@echo "I/O check not implemented for this example"
