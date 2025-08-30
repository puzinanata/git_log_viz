FROM ubuntu:latest

ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/home/puzinanata/git_log_viz

COPY / $APP_HOME

RUN cd $APP_HOME && \
  /bin/bash deployment_vm/deploy_docker.sh



#/git_log_viz/myproject/static/


# cd /git_log_viz &&\
#   /bin/bash deploy.sh
