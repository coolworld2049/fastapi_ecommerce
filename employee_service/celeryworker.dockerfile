FROM python:3.11

COPY employee_service/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /employee_service/requirements.txt

COPY employee_service /app

WORKDIR /app

ENV PYTHONPATH=/app

ENV C_FORCE_ROOT=1

COPY employee_service/worker-start.sh /worker-start.sh

RUN chmod +x /worker-start.sh

CMD ["bash", "/worker-start.sh"]
