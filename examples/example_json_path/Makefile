.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_jsonpath_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && echo '{"store":{"book":[{"title":"Book1"},{"title":"Book2"}]}}' | python jsonpath_cli.py '$.store.book[*].title'

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile jsonpath_cli.py -o json_path

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f json_path

io-check:
	@echo "I/O check not implemented for this example"
