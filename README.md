[![Build Status](https://circleci.com/gh/cloudify-examples/docker-swarm-blueprint.svg?style=shield&circle-token=:circle-token)](https://circleci.com/gh/cloudify-examples/docker-swarm-blueprint)

## Docker Swarm Example Blueprint

The blueprints in this project provide orchestration for starting, healing, and scaling a Docker Swarm cluster on Openstack and AWS.

### Openstack

There are 3 blueprints for Openstack, with slightly different use cases.

* **local-openstack-swarm-blueprint.yaml** : a cfy local blueprint that orchestrates setup and teardown of the cluster without a manager
* **openstack-swarm-blueprint.yaml** : an Openstack blueprint that orchestrates setup and teardown of the cluster with a manager
* **openstack-swarm-scale-blueprint.yaml** : an Openstack blueprint that orchestrates setup, teardown, autohealing, and autoscaling of the cluster

### AWS

There are 2 blueprints for AWS, with slightly different use cases.

* **aws-swarm-blueprint.yaml** : an AWS blueprint that orchestrates setup and teardown of the cluster with a manager
* **aws-swarm-scale-blueprint.yaml** : an AWS blueprint that orchestrates setup, teardown, autohealing, and autoscaling of the cluster

### Prerequisites

These blueprints have only been tested against an Ubuntu 14.04 image with 2GB of RAM.  The image used must be pre-installed with Docker 1.12, although, we do try to install Docker if it is not installed.  Any image used should have passwordless ssh, and passwordless sudo with `requiretty` false or commented out in sudoers.  Also required is an Openstack cloud environment or an AWS account.  The blueprints were tested on Openstack Kilo and AWS.

### Cloudify Version

These blueprints were tested on Cloudify 4.0.

### Cloudify Manager Operation

#### openstack-swarm-blueprint.yaml instructions

* Start a Cloudify 4.0 [manager](http://docs.getcloudify.org/4.0.0/manager/bootstrapping/).
* Edit the `inputs/openstack.yaml` file to add image, flavor, and user name (probably ubuntu).
* run `cfy install openstack-swarm-blueprint.yaml -i inputs/openstack.yaml -b swarm`

This will create the Swarm cluster.  The manager node is assigned a public ip.  You can see it by running `cfy deployments outputs swarm`.

To tear down the cluster, run `cfy uninstall swarm -p ignore_failure=true`

#### openstack-swarm-scale-blueprint.yaml instructions

* Start a Cloudify 4.0 [manager](http://docs.getcloudify.org/4.0.0/manager/bootstrapping/).
* Edit the `inputs/openstack.yaml` file to add image, flavor, and user name (probably ubuntu).
* run `cfy install openstack-swarm-scale-blueprint.yaml -i inputs/openstack.yaml -b swarm-scale`

This will create the Swarm cluster.  The manager node is assigned a public ip.  You can see it by running `cfy deployments outputs swarm-scale`.

To see autohealing in action, go to the Openstack Horizon dashboard and terminate the worker.  Then go to the Cloudify UI deployments tab.  See the `heal` workflow begin and restore the missing node.

To see autoscaling in action:
* ssh to the Cloudify manager: `cfy ssh`
* ssh to a swarm worker: `sudo ssh -i <private-key-path> ubuntu@<worker-ip>`
* run the built in load generator container: `sudo docker service create --constraint 'node.role == worker' --restart-condition none stress /start.sh`
* Then go to the Cloudify UI deployments tab.  See the `scale` workflow begin and grow the cluster.

In a few minutes, the cluster will scale down to it's original size (one worker) due to the scale down policy in the blueprint.

To tear down the cluster, run `cfy uninstall swarm-scale -p ignore_failure=true`

#### aws-swarm-blueprint.yaml instructions

* Start a Cloudify 4.0 [manager](http://docs.getcloudify.org/4.0.0/manager/bootstrapping/).
* Edit the `inputs/aws.yaml.example` file to add your VPC, subnets, CIDRs, regions and AMI.
* run `cfy install aws-swarm-blueprint.yaml -i inputs/aws.yaml.example -b swarm`

This will create the Swarm cluster.  The manager node is assigned a public ip.  You can see it by running `cfy deployments outputs swarm`.

To tear down the cluster, run `cfy uninstall swarm -p ignore_failure=true`

#### aws-swarm-scale-blueprint.yaml instructions

* Start a Cloudify 4.0 [manager](http://docs.getcloudify.org/4.0.0/manager/bootstrapping/).
* Edit the `inputs/aws.yaml.example` file to add your VPC, subnets, CIDRs, regions and AMI.
* run `cfy install aws-swarm-scale-blueprint.yaml -i inputs/aws.yaml.example -b swarm-scale`

This will create the Swarm cluster.  The manager node is assigned a public ip.  You can see it by running `cfy deployments outputs swarm-scale`.

To see autohealing in action, go to the Openstack Horizon dashboard and terminate the worker.  Then go to the Cloudify UI deployments tab.  See the `heal` workflow begin and restore the missing node.

To see autoscaling in action:
* ssh to the Cloudify manager: `cfy ssh`
* ssh to a swarm worker: `sudo ssh -i <private-key-path> ubuntu@<worker-ip>`
* run the built in load generator container: `sudo docker service create --constraint 'node.role == worker' --restart-condition none stress /start.sh`
* Then go to the Cloudify UI deployments tab.  See the `scale` workflow begin and grow the cluster.

In a few minutes, the cluster will scale down to it's original size (one worker) due to the scale down policy in the blueprint.

To tear down the cluster, run `cfy uninstall swarm-scale -p ignore_failure=true`

### CFY-local Operation

#### local-openstack-swarm-blueprint.yaml instructions

** This section has not been updated for Cloudify 4.0 **

* Clone the repo to a system that access to the target Openstack cloud
* Edit the `inputs/local.yaml` file as follows:
 * image : the image id on Openstack of the Ubuntu 14.04 image
 * flavor : the Openstack flavor id
 * ssh_user : the ssh user to log into the instances (probably `ubuntu`)
 * ssh_keyfile : the path to the key used to ssh to the instance
 * ssh_keyname : the name of the key in openstack
* run `cfy local install-plugins -p local-openstack-swarm-blueprint.yaml`
* run `cfy local execute -w install --task-retries 10`

This will create the Swarm cluster.  The manager node is assigned a public ip.  You can see it by running `cfy local outputs`.

To tear down the cluster, run `cfy local execute -w uninstall --task-retries 10`.


