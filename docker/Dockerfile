ARG include
ARG package

FROM python:3.10 as tp1-poetry

# RUN apt-get update && apt-get install -y curl
RUN curl -sSL https://install.python-poetry.org | python -
ENV PATH="${PATH}:/root/.local/bin"

FROM tp1-poetry as tp1-include-lib

COPY tp1/lib /tp1/lib

FROM tp1-include-lib as tp1-include-middleware

COPY tp1/middleware /tp1/middleware

FROM tp1-include-${include} as final

WORKDIR /tp1/${package}
COPY tp1/${package} /tp1/${package}
RUN poetry install --only main

ENTRYPOINT [ "poetry", "run", "${package}" ]
