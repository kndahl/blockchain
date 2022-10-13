FROM tiangolo/uvicorn-gunicorn:python3.9
WORKDIR /worker
COPY ./requirements.txt /worker/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /worker/requirements.txt
COPY ./worker.py /worker/
COPY ./service.py /worker/
COPY ./colors.py /worker/
EXPOSE 3000

CMD ["uvicorn", "service:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "3000"]