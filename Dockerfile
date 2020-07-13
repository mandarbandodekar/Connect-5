FROM python:3.7-slim

# Set the working directory to /app
WORKDIR /app
ADD requirements.txt /app
RUN pip3 install -r requirements.txt


ADD templates /app/templates
ADD app.py /app
ADD utils.py /app


EXPOSE 7000

# Run app.py when the container launches
ENTRYPOINT ["python3", "app.py"]
