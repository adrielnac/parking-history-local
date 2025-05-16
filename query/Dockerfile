FROM python:3.13-slim

WORKDIR /app
RUN mkdir /data
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "query_parking.py"]
