.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_text_parse_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python text_parse_cli.py count "Hello World" --words

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile text_parse_cli.py -o text_parse

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f text_parse

io-check:
	@echo "I/O check not implemented for this example"
