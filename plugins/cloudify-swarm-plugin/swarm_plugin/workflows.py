from cloudify.decorators import workflow
from cloudify.workflows import ctx
from cloudify import manager
import re
import os
from fabric.api import run,env,put


#
# Scale a replication controller
#
@workflow
def kube_scale(**kwargs):
  setfabenv(kwargs)

  #get resource name
  nodename=kwargs['name']
  node=ctx.get_node(nodename)
  name=node.properties['name']
  amount=0

  #if the request is an increment, get current value
  if(kwargs['amount'][0]=='+' or kwargs['amount'][0]=='-'):
    output=run("./kubectl -s http://localhost:8080 get rc --no-headers {}".format(name))
    curinstances=int(output.stdout.split()[4])
    inc=int(kwargs['amount'])
    amount=curinstances+inc
  else:
    amount=int(kwargs['amount'])

  with open("/tmp/log","a") as f:
    f.write("running: ./kubectl -s http://localhost:8080 scale --replicas={} rc {}".format(amount,name))
  run("./kubectl -s http://localhost:8080 scale --replicas={} rc {}".format(amount,name))

#
# Run an image on the cluster pointed to by the master arg
#
@workflow
def kube_create(**kwargs):
  setfabenv(kwargs)
  url=kwargs['url']
  #get manifest
  if(url[0:4]=='http'):
    #external
    run("wget -O /tmp/manifest.yaml "+url)
  else:
    #in blueprint dir
    with open("/tmp/log","a") as f:
      f.write("getting manifest\n")

    res=manager.download_blueprint_resource(ctx.blueprint.id,url,ctx.logger)
    
    put(res,"/tmp/manifest.yaml")

  run("./kubectl -s http://localhost:8080 create -f /tmp/manifest.yaml")

#
# Run an image on the cluster pointed to by the master arg
#
@workflow
def kube_run(**kwargs):
  setfabenv(kwargs)
  optstr=buildopts(kwargs,{"dry_run":"dry-run"},{"port":"not _val_ == -1"},["dry_run"],['name','master'])
  ctx.logger.info("Running: {}".format(optstr))
  run("./kubectl -s http://localhost:8080 run "+" "+kwargs['name']+optstr)

#
# Expose an app
#
@workflow
def kube_expose(**kwargs):
  setfabenv(kwargs)
  optstr=buildopts(kwargs,{"target_port":"target-port","service_name":"service-name"},{"target_port":"not _val_ == -1"},[],['name','master','resource'])
  runstr="./kubectl -s http://localhost:8080 expose {} {} {}".format(kwargs['resource'],kwargs['name'],optstr)
  ctx.logger.info("Running: {}".format(runstr))
  run(runstr)
  
#
# Stop a resource (by name)
#
@workflow
def kube_stop(**kwargs):
  setfabenv(kwargs)
  optstr=buildopts(kwargs,{},{},["all"],['name','master','resource'])
  runstr="./kubectl -s http://localhost:8080 stop {} {} {}".format(kwargs['resource'],kwargs['name'],optstr)
  ctx.logger.info("Running: {}".format(runstr))
  run(runstr)
  
#
# Delete a resource (by name)
#
@workflow
def kube_delete(**kwargs):
  setfabenv(kwargs)
  optstr=buildopts(kwargs,{},{},["all"],['name','master','resource'])
  runstr="./kubectl -s http://localhost:8080 delete {} {} {}".format(kwargs['resource'],kwargs['name'],optstr)
  ctx.logger.info("Running: {}".format(runstr))
  with open("/tmp/log","a") as f:
    f.write("executing {}\n".format(runstr))
  run(runstr)

##################################################
#
# UTILITY
#
##################################################

# Construct the fabric environment from the supplied master
# node in kwargs
def setfabenv(kwargs):
  fabenv={}
  master=get_ip(kwargs['master'])
  masternode=ctx.get_node(kwargs['master'])
  if(masternode.type=='cloudify.nodes.DeploymentProxy'):
    #grab proper ip, assumes relationship has copied properties to instance
    fabenv['host_string']=kwargs['ssh_user']+'@'+master
    fabenv['port']=kwargs.get('ssh_port','22')
    fabenv['user']=kwargs['ssh_user']
    fabenv['key_filename']=kwargs['ssh_keyfilename']
  else:
    #requires ssh info be defined on master node
    masternode=ctx.get_node(kwargs['master'])
    fabenv['host_string']=masternode.properties['ssh_user']+'@'+masternode.properties['ip']
    fabenv['port']=masternode.properties['ssh_port']
    fabenv['user']=masternode.properties['ssh_user']
    fabenv['password']=masternode.properties['ssh_password']
    fabenv['key_filename']=masternode.properties['ssh_keyfilename']
  env.update(fabenv)

# utility class to process options in the form
# specific to kubectl
class Option(object):
  def __init__(self,arg,val,cond=None,option_name=None):
    self._arg=arg
    self._option_name=option_name
    self._cond=cond
    self._val=val

  def __str__(self):
    if(self._cond):
      _val_=self._val
      if(not eval(self._cond)):
        return ''
    return "--"+(self._option_name or self._arg)+"="+str(self._val)

def buildopts(kwargs,namedict={},conddict={},flags=[],ignore=[]):
  ignore=ignore+['ssh_user','ssh_keyfilename']
  outstr=''
  for k,v in kwargs.iteritems():
    if(k.startswith('_') or k=='ctx' or k in ignore):
      continue
    if(not v):
      continue
    if(k in conddict):
      _val_=v
      if(not eval(conddict[k])):
        continue
    if(k in namedict):
      outstr=outstr+" --"+namedict[k]
    else:
      outstr=outstr+" --"+k
    if(not k in flags):
      outstr=outstr+"="+str(v)
  return outstr


def get_ip(master):
  node=ctx.get_node(master)
  if(ctx.local):
    return ctx.get_node(master).properties['ip']
  else:
    # use default instance ([0])
    instance=node.instances.next()._node_instance
    if(node.type=='cloudify.nodes.DeploymentProxy'):
      r=re.match('.*://(.*):(.*)',instance.runtime_properties['kubernetes_info']['url'])
      with open("/tmp/log","a") as f:
        f.write("instance runtime properties:"+str(instance.runtime_properties))
        f.write("  ip="+r.group(1))
      return(r.group(1))
    else:
      return(instance.runtime_properties['ip'])
