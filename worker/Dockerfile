# this dockerfile expects to be executed from the
# root of the repository
FROM poetry-base-tp1

WORKDIR /tp1/worker
COPY ./common/ /tp1/common
COPY ./middleware/ /tp1/middleware
COPY ./worker/ /tp1/worker
RUN poetry install

ENTRYPOINT [ "poetry", "run", "worker" ]
