.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_markdown_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && echo "# Hello\n**bold**" | python markdown_cli.py -

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile markdown_cli.py -o markdown_parser

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f markdown_parser

io-check:
	@echo "I/O check not implemented for this example"
