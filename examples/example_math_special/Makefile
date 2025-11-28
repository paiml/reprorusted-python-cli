.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_special_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python special_cli.py hypot 3 4

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile special_cli.py -o math_special

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f math_special

io-check:
	@echo "I/O check not implemented for this example"
