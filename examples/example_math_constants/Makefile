.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_constants_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python constants_cli.py circle 5 --area --circumference

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile constants_cli.py -o math_constants

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f math_constants

io-check:
	@echo "I/O check not implemented for this example"
