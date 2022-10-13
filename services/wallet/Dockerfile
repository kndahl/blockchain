FROM tiangolo/uvicorn-gunicorn:python3.9
WORKDIR /wallet
COPY ./requirements.txt /wallet/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /wallet/requirements.txt
COPY ./wallet.py /wallet/
COPY ./service.py /wallet/
COPY ./colors.py /wallet/
EXPOSE 9090

CMD ["uvicorn", "service:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "9090"]