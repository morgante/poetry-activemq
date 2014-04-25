# DOCKER-VERSION 0.8.0
FROM		shykes/pybuilder

# Install requirements
ADD 		./requirements.txt /requirements.txt
RUN 		pip install -r /requirements.txt

# Add source
ADD 		. /src

# Expose port
EXPOSE 		5000

# Run it
WORKDIR		/src

ENTRYPOINT ["python"]
CMD ["server.py"]