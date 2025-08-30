#!/bin/bash

#1 Step: build/rebuild container
docker build -t git_log_viz .

#2 Step: force stop the previous version of the container
docker kill git_log_viz || true
docker rm git_log_viz || true

#3 Step: run new container
docker run -d \
    --name git_log_viz \
    --network custom-network \
    --ip 10.0.0.102 \
    --entrypoint /docker-entrypoint.sh \
    -v /var/lib/git_repos:/var/lib/git_repos \
    git_log_viz:latest
