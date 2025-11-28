.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_file_write_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python file_write_cli.py write /tmp/test_write.txt "Hello World"

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile file_write_cli.py -o file_write

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f file_write

io-check:
	@echo "I/O check not implemented for this example"
