FROM python:3.7-alpine

WORKDIR /app

COPY OpenWeatherMapLogger.py /app
COPY settings.py /app
COPY requirements.txt /app

RUN pip install -r requirements.txt

CMD ["python", "-u", "OpenWeatherMapLogger.py"]