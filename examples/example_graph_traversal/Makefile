.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_graph_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python graph_cli.py a-b b-c c-d a-d --mode bfs --start a

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile graph_cli.py -o graph_traversal

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f graph_traversal

io-check:
	@echo "I/O check not implemented for this example"
