FROM python:3.10.7

COPY . /app

WORKDIR /app

# import dependencies and build the application 
RUN pip install -r requirements.txt

EXPOSE 3111

# command to run on container start 
CMD [ "python", "init_db.py"]
CMD [ "python", "app.py" ]
