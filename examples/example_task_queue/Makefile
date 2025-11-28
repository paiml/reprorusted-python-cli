.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_queue_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python queue_cli.py add "Test Task" -p 5

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile queue_cli.py -o task_queue

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f task_queue queue.json

io-check:
	@echo "I/O check not implemented for this example"
