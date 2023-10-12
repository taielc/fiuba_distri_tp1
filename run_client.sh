#!/bin/bash

# lib and client volumes can be removed on built image
docker run -it --rm --network=docker_default \
  --volume .data:/.data \
  --volume tp1/lib/src/:/tp1/lib/src/ \
  --volume tp1/client/src/:/tp1/client/src/ \
  tp1-client
