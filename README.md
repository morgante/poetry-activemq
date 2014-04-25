

To use this example, just follow these steps:

1. Load a Docker container for ActiveMQ:
	
	docker pull viliusl/ubuntu-activemq-server

2. Start the ActiveMQ container:
	
	docker run --name activemq -p 61613 -d viliusl/ubuntu-activemq-server

3. Build the example:

	docker build -t morgante/poetry .

4. Run the example:

	docker run --link activemq:activemq -v /var/code/CS-209/poetry-activemq:/src -i -t morgante/poetry server.py