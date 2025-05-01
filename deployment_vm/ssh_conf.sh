#!/bin/bash

# Turn on debugging mode
set -x

# Define your project and VM info
PROJECT_ID="some_project-id"
VM_NAME="instance-number"
ZONE="some-zone"
USER="some_user"

# Step 0: install and run  gcloud
brew install --cask google-cloud-sdk

#run gcloud:
source "$(brew --prefix)/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/path.bash.inc"

# login to your google account (redirect to browser to authorize ):
gcloud auth login

# Step 1: set project
gcloud config set project "$PROJECT_ID"

# Step 2: connect with my test VM by SSH
gcloud compute ssh "$USER@$VM_NAME" --zone="$ZONE"
