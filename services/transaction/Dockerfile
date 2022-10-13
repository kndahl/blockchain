FROM tiangolo/uvicorn-gunicorn:python3.9
WORKDIR /transaction
COPY ./requirements.txt /transaction/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /transaction/requirements.txt
COPY ./transactions.py /transaction/
COPY ./service.py /transaction/
COPY ./colors.py /transaction/
EXPOSE 7070

CMD ["uvicorn", "service:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "7070"]