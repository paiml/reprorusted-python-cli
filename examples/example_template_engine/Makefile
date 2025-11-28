.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_template_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python template_cli.py -t "Hello {{ name }}!" -c '{"name": "World"}'

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile template_cli.py -o template_engine

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f template_engine

io-check:
	@echo "I/O check not implemented for this example"
