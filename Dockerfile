FROM python:3.7-slim
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
COPY . /code/
RUN pip install numpy \
    && pip install pandas \
    && pip install -r requirements.txt \