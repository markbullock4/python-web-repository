FROM amazonlinux:2
COPY . /app
WORKDIR /app
ENV POSTGRES_ENV = 'prod'
RUN yum install python3-pip -y
RUN python3 --version
#RUN yum install python34 -y
RUN pip3 install flask  
RUN pip3 install psycopg2-binary 	
RUN pip3 install flask-sqlalchemy 
EXPOSE 5000
CMD python3 app.py

