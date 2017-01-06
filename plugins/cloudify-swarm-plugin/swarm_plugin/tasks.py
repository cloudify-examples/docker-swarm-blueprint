########
# Copyright (c) 2015 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

#
# Swarm plugin implementation
#
import requests
import json
import fabric
from util import *
from cloudify.decorators import operation
from cloudify import ctx,manager,utils
from cloudify.exceptions import NonRecoverableError
from fabric.api import run,env,put,sudo


# Called when connecting to master.  Gets ip and port
@operation
def connect_manager(**kwargs):
  ctx.logger.info("in connect_master")
  info = requests.get('http://{}:{}/swarm'.format(ctx.node.properties['ip'],ctx.node.properties['port'])).json()
  ctx.instance.runtime_properties['swarm_info']=info
  ctx.logger.info("info:{}".format(ctx.instance.runtime_properties['swarm_info']))

@operation
def start_service(**kwargs):
  ctx.logger.info("in start_service")

  if ctx.node.properties['compose_file'] != '':
    # get file, transfer to master, and run
    ctx.logger.info("getting compose file:{}".format(ctx.node.properties['compose_file']))
    path=ctx.download_resource(ctx.node.properties['compose_file'])
    if not 'mgr_ssh_user' in ctx.instance.runtime_properties:
      raise NonRecoverableError('ssh user not specified') 
    if not 'mgr_ssh_keyfile' in ctx.instance.runtime_properties:
      raise NonRecoverableError('ssh keyfile not specified') 
    setfabenv(ctx)
    ctx.logger.info("putting compose file on manager")
    put(path,"/tmp/compose.in")
    ctx.logger.info("calling compose")
    sudo("/usr/local/bin/docker-compose  -H localhost:2375 -f /tmp/compose.in up")

  else:
    body={}
    body['Name']=ctx.node.properties['name']
    body['TaskTemplate']={}
    body['TaskTemplate']['Placement']=ctx.node.properties['placement']
    body['TaskTemplate']['Limits']=ctx.node.properties['limits']
    body['Mode']={}
    body['Mode']['Replicated']={}
    body['Mode']['Replicated']['Replicas']=ctx.node.properties['replicas']
    body['EndpointSpec']={}
    body['EndpointSpec']['Ports']=[]
    if 'labels' in ctx.node.properties:
      body['Labels']=ctx.node.properties['labels']

    #containers, volumes
    for k,v in ctx.instance.runtime_properties.iteritems():
      if str(k).startswith("container_"):
        body['TaskTemplate']['ContainerSpec']=camelmap(v)
      elif str(k).startswith("port_"):  
        body['EndpointSpec']={} if not 'EndpointSpec' in body else body['EndpointSpec']
        key=body['EndpointSpec']['Ports']=[] if not 'Ports' in body['EndpointSpec'] else body['EndpointSpec']['Ports']
        key.append(camelmap(v))
    ctx.logger.info("BODY={}".format(json.dumps(body)))
    resp =requests.post('http://{}:{}/services/create'.format(ctx.instance.runtime_properties['ip'],ctx.instance.runtime_properties['port']),data=json.dumps(body),headers={'Content-Type':'application/json'})

    print "RESP={} {}".format(resp.status_code,resp.text)
    if resp.status_code != 201:
      raise NonRecoverableError(resp.text) 
 
    # get service id
    resp=json.loads(resp.text)
    ctx.instance.runtime_properties['service_id']=resp['ID']

@operation
def add_volume(**kwargs):
  ctx.logger.info("in add_volume")
  key='volume_{}'.format(ctx.target.instance.id)
  ctx.source.instance.runtime_properties[key]=ctx.target.node.properties

@operation
def add_container(**kwargs):
  ctx.logger.info("in add_container")
  key=ctx.source.instance.runtime_properties['container_{}'.format(ctx.target.instance.id)]={}
  key['Image']=ctx.target.node.properties['image']
  for k,v in ctx.target.instance.runtime_properties.iteritems():
    if str(k).startswith("volume_"):
      if not 'Mounts' in key:
        key['Mounts']=[]
      key['Mounts'].append(camelmap(v))

@operation
def add_port(**kwargs):
  ctx.logger.info("in add_port")
  ctx.source.instance.runtime_properties['port_{}'.format(ctx.target.instance.id)]=ctx.target.node.properties

@operation
def add_microservice(**kwargs):
  ctx.logger.info("in ad_microserivce")
  ctx.source.instance.runtime_properties['ip']=ctx.target.node.properties['ip']
  ctx.source.instance.runtime_properties['port']=ctx.target.node.properties['port']
  ctx.logger.info("MICROSERVICE VALS={}".format(ctx.source.instance.runtime_properties['ip'],ctx.source.instance.runtime_properties['port']))
  if 'ssh_user' in ctx.target.node.properties and 'ssh_keyfile' in ctx.target.node.properties:
    ctx.source.instance.runtime_properties['mgr_ssh_user']=ctx.target.node.properties['ssh_user']
    ctx.source.instance.runtime_properties['mgr_ssh_keyfile']=ctx.target.node.properties['ssh_keyfile']

@operation
def rm_service(**kwargs):
  ctx.logger.info("in rm_microservice")
  id=ctx.instance.runtime_properties['service_id']
  resp = requests.delete('http://{}:{}/services/{}'.format(ctx.instance.runtime_properties['ip'],ctx.instance.runtime_properties['port'],id))
  if resp.status_code != 200:
    raise NonRecoverableError(resp.text) 

# Construct the fabric environment from the supplied master
# node in kwargs
def setfabenv(ctx):
  fabenv={}
  fabenv['host_string']=ctx.instance.runtime_properties['mgr_ssh_user']+'@'+ctx.instance.runtime_properties['ip']
  fabenv['key_filename']=ctx.instance.runtime_properties['mgr_ssh_keyfile']
  env.update(fabenv)

