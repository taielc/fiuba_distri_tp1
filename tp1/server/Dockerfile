# this dockerfile expects to be executed from the
# root of the repository
FROM poetry-base-tp1

WORKDIR /tp1/server
COPY ./lib/ /tp1/lib
COPY ./middleware/ /tp1/middleware
COPY ./server/ /tp1/server
RUN poetry install

ENTRYPOINT [ "poetry", "run", "server" ]
