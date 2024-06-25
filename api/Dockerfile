FROM python:3.10.7-slim

COPY . /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

ADD https://github.com/vishnubob/wait-for-it/raw/master/wait-for-it.sh /usr/wait-for-it.sh
RUN chmod +x /usr/wait-for-it.sh

EXPOSE 5050

CMD /usr/wait-for-it.sh db:5432 -- gunicorn -w 4 -b 0.0.0.0:5050 main:app
