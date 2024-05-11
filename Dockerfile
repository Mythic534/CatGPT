FROM python:3.10-alpine

RUN mkdir -p /app
ADD . /app
WORKDIR /app

RUN pip install pipenv
RUN pipenv install --deploy --system
CMD ["python", "main.py"]