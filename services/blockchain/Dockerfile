FROM tiangolo/uvicorn-gunicorn:python3.9
WORKDIR /blockchain
COPY ./requirements.txt /blockchain/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /blockchain/requirements.txt
COPY ./blockchain.py /blockchain/
COPY ./service.py /blockchain/
COPY ./colors.py /blockchain/
COPY ./registration.py /blockchain/
EXPOSE 8000

CMD ["uvicorn", "service:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]