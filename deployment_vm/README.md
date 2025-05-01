### Option 1. Run project on new VM to run following commands in terminal on VM:
git clone "https://github.com/puzinanata/git_log_viz"

cd git_log_viz/deployment_vm/

bash deploy.sh

#### After deployment test site will be available here: 
http://testgitreport.duckdns.org/

### Option 2. Run project from local terminal via SSH (gcloud):
#### a. For first time use script ssh_conf, set up your project and VM info
cd git_log_viz/deployment_vm/

bash ssh_conf.sh

#### then:
cd git_log_viz/deployment_vm/
bash deploy.sh

#### b. For next times use SSH -connection:
gcloud compute ssh "$USER@$VM_NAME" --zone="$ZONE"

where 
PROJECT_ID="some_project-id"
VM_NAME="instance-number"
ZONE="some-zone"
USER="some_user"


