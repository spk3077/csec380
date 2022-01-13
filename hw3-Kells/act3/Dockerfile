FROM python:3.9
WORKDIR /usr/src/app
COPY . .
RUN apt-get update \
    && apt-get install -y vim python3-bs4
    
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python3", "act3.py"]