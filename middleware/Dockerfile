FROM python:3.10.6

RUN mkdir /app 
COPY . /app
COPY pyproject.toml /app
COPY ./poetry.lock /app

WORKDIR /app

ENV PYTHONPATH=${PYTHONPATH}:${PWD} 
ENV POETRY_VERSION=1.5.1

# Install Python env
RUN pip3 install "poetry==$POETRY_VERSION"
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

CMD ["poetry", "run", "python", "src/main.py"]