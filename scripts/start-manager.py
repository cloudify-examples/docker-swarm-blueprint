import subprocess
import os
import time
from cloudify import ctx
from cloudify.exceptions import RecoverableError, NonRecoverableError
from cloudify.state import ctx_parameters as inputs

output,error=0,0

process=subprocess.Popen(
  ['sudo','docker','swarm','init','--advertise-addr',inputs['ip']],
  stdout=subprocess.PIPE,
  stderr=subprocess.PIPE
)

if process.returncode:
  output,error=process.communicate()
  raise NonRecoverableError(
    'Failed to init manager',
    'Output: {0}',
    'Error: {1}'.format(output,error)
  )

for i in range(0,10):
  process=subprocess.Popen(
    ['sudo','docker','swarm','join-token','-q','manager'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
  )
  if process.returncode:
    output,error=process.communicate()
    raise NonRecoverableError(
      'Failed to get manager token',
      'Output: {0}',
      'Error: {1}'.format(output,error)
    )

  output,error=process.communicate()
  if(len(output)>0):
    break
  ctx.logger.info("got no output, retrying...")
  time.sleep(1)

ctx.logger.info("storing manager token = {}".format(output))
ctx.instance.runtime_properties['manager_token']=output

process=subprocess.Popen(
  ['sudo','docker','swarm','join-token','-q','worker'],
  stdout=subprocess.PIPE,
  stderr=subprocess.PIPE
)
if process.returncode:
  output,error=process.communicate()
  raise NonRecoverableError(
    'Failed to get worker token',
    'Output: {0}',
    'Error: {1}'.format(output,error)
  )
output,error=process.communicate()
ctx.instance.runtime_properties['worker_token']=output
ctx.logger.info("storing worker token = {}".format(ctx.instance.runtime_properties['worker_token']))

# If there are existing nodes, tell them to rejoin (heal scenario)

try:
  rel=None
  for rel in ctx.instance.relationships:
    if rel.type == "cloudify.relationships.contained_in":
      break
  if rel == None:
    raise NonRecoverableError("contained in rel not found")

  for rel2 in rel.target.instance.relationships:
    if rel2.type == "cloudify.relationships.contained_in":
      break
  if rel2 == None:
    raise NonRecoverableError("contained in rel/rel not found")

  rel2.target.instance.runtime_properties['manager_token']=ctx.instance.runtime_properties['manager_token']

except Exception as e:
  ctx.logger.error("caught exception {}".format(e.message))
  pass
