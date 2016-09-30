## Docker Swarm Example Blueprint

The blueprints in this project provide orchestration for starting, healing, and scaling a Docker Swarm cluster on Openstack.  There are 3 blueprints, with slightly different use cases:
* **swarm-local-blueprint.yaml** : a cfy local blueprint that orchestrates setup and teardown of the cluster without a manager
* **swarm-openstack-blueprint.yaml** : an Openstack blueprint that orchestrates setup and teardown of the cluster with a manager
* **swarm-scale-blueprint.yaml** : an Openstack bluieprint that orchestrates setup, teardown, autohealing, and autoscaling of the cluster

### Prerequisites

These blueprints have only been tested against an Ubuntu 14.04 image with 2GB of RAM.  The image used must be pre-installed with Docker 1.12.  Any image used should have passwordless ssh, and passwordless sudo with `requiretty` false or commented out in sudoers.  Also required is an Openstack cloud environment.  The blueprints were tested on Openstack Kilo.

### Cloudify Version

These blueprints were tested on Cloudify 3.4.0.

### Operation

#### swarm-local-blueprint.yaml instructions

* Clone the repo to a system that access to the target Openstack cloud
* Edit the `inputs/local.yaml` file as follows:
 * image : the image id on Openstack of the Ubuntu 14.04 image
 * flavor : the Openstack flavor id
 * ssh_user : the ssh user to log into the instances (probably `ubuntu`)
 * ssh_keyfile : the path to the key used to ssh to the instance
 * ssh_keyname : the name of the key in openstack
* run `cfy local install-plugins -p swarm-local-blueprint.yaml`
* run `cfy local execute -w install --task-retries 10`

This will create the Swarm cluster.  The manager node is assigned a public ip.  You can see it by running `cfy local outputs`.

To tear down the cluster, run `cfy local execute -w uninstall --task-retries 10`.

#### swarm-openstack-blueprint.yaml instructions

* Start a Cloudify 3.4.0 [manager](http://docs.getcloudify.org/3.4.0/manager/bootstrapping/).
* Edit the `inputs/openstack.yaml` file to add image, flavor, and user name (probably ubuntu).
* run `cfy blueprints upload -b swarm -p swarm-openstack-blueprint.yaml`
* run `cfy deployments create -b swarm -d swarm -i input/openstack.yaml`
* run `cfy executions start -d swarm -w install`

This will create the Swarm cluster.  The manager node is assigned a public ip.  You can see it by running `cfy deployments outputs -d swarm`.

To tear down the cluster, run `cfy executions start -d swarm -w uninstall`

#### swarm-scale-blueprint.yaml instructions

* Start a Cloudify 3.4.0 [manager](http://docs.getcloudify.org/3.4.0/manager/bootstrapping/).
* Edit the `inputs/openstack.yaml` file to add image, flavor, and user name (probably ubuntu).
* run `cfy blueprints upload -b swarm -p swarm-openstack-blueprint.yaml`
* run `cfy deployments create -b swarm -d swarm -i input/openstack.yaml`
* run `cfy executions start -d swarm -w install`

This will create the Swarm cluster.  The manager node is assigned a public ip.  You can see it by running `cfy deployments outputs -d swarm`.

To see autohealing in action, go to the Openstack Horizon dashboard and terminate the worker.  Then go to the Cloudify UI deployments tab.  See the `heal` workflow begin and restore the missing node.

To see autoscaling in action:
* ssh to the Cloudify manager: `cfy ssh`
* ssh to the swarm manager: `sudo ssh -i /root/.ssh/agent_key.pem ubuntu@<manager-ip>`
* run the built in load generator container: `sudo docker service create --constraint 'node.role == worker' --restart-condition none stress /start.sh`
* Then go to the Cloudify UI deployments tab.  See the `scale` workflow begin and grow the cluster.

In a few minutes, the cluster will scale down to it's original size (one worker) due to the scale down policy in the blueprint.

To tear down the cluster, run `cfy executions start -d swarm -w uninstall`
