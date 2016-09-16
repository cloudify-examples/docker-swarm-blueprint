import subprocess
import os
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
ctx.logger.info("storing master token = {}".format(output))
ctx.instance.runtime_properties['master_token']=output

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

