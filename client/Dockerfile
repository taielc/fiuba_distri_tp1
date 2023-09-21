# this dockerfile expects to be executed from the
# root of the repository
FROM poetry-base-tp1

WORKDIR /tp1/client
COPY ./common/ /tp1/common
COPY ./client/ /tp1/client
RUN poetry install

ENTRYPOINT [ "poetry", "run", "client" ]
