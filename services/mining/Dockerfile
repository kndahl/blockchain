FROM python:3.9
WORKDIR /mining
COPY ./requirements.txt /mining/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /mining/requirements.txt
COPY ./mining.py /mining/

CMD [“python3”, mining.py”] 