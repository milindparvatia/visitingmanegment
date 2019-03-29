FROM python:3.7-slim
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
COPY . /code/

# Update the default application repository sources list
RUN pip install -r requirements.txt
# RUN sed $'s/\r$//' ./start.sh > ./start.Unix.sh
# expose the port 8000
EXPOSE 8000

# define the default command to run when starting the container
CMD ["gunicorn", "--chdir", "projectvisitor", "--bind", ":8000", "projectvisitor.wsgi:application"]