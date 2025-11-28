.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_closure_capture_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python closure_capture_cli.py adder 5 10

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile closure_capture_cli.py -o closure_capture

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f closure_capture

io-check:
	@echo "I/O check not implemented for this example"
