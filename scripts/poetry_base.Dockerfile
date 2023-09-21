FROM python:3.10

# RUN apt-get update && apt-get install -y curl
RUN curl -sSL https://install.python-poetry.org | python -
ENV PATH="${PATH}:/root/.local/bin"
