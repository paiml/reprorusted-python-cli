.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_file_text_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python file_text_cli.py read /etc/hostname

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile file_text_cli.py -o file_text

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f file_text

io-check:
	@echo "I/O check not implemented for this example"
