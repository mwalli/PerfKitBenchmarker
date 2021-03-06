# Copyright 2014 PerfKitBenchmarker Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utilities for working with SoftLayer resources."""

import re
import string

from perfkitbenchmarker import errors
from perfkitbenchmarker import flags
from perfkitbenchmarker import vm_util

SoftLayer_PATH = 'slcli'
SoftLayer_PREFIX = [SoftLayer_PATH]
FLAGS = flags.FLAGS


def IsRegion(zone_or_region):
  """Returns whether "zone_or_region" is a region."""
  if not re.match(r'[a-z]{3}[0-9]{2}$', zone_or_region):
    raise ValueError(
        '%s is not a valid SoftLayer zone or region name' % zone_or_region)
  return zone_or_region[-1] in string.digits


def GetRegionFromZone(zone_or_region):
  """Returns the region a zone is in (or "zone_or_region" if it's a region)."""
  if IsRegion(zone_or_region):
    return zone_or_region
  return zone_or_region[:-1]


def AddTags(resource_id, region, **kwargs):
  """Adds tags to an SoftLayer resource created by PerfKitBenchmarker.

  Args:
    resource_id: An extant SoftLayer resource to operate on.
    region: The SoftLayer region 'resource_id' was created in.
    **kwargs: dict. Key-value pairs to set on the instance.
      """
  if not kwargs:
    return

  tag_cmd = SoftLayer_PREFIX + [
      'vs',
      'edit']
  for key, value in kwargs.iteritems():
    tag_cmd.append('--tag {0}:{1}'.format(key, value))
  tag_cmd.append('{0}'.format(resource_id))
  print "skipping tag in util"
  #IssueRetryableCommand(tag_cmd)


def AddDefaultTags(resource_id, region):
  """Adds tags to an SoftLayer resource created by PerfKitBenchmarker.

  By default, resources are tagged with "owner" and "perfkitbenchmarker-run"
  key-value
  pairs.

  Args:
    resource_id: An extant SoftLayer resource to operate on.
    region: The SoftLayer region 'resource_id' was created in.
  """
  tags = {'owner': FLAGS.owner, 'perfkitbenchmarker-run': FLAGS.run_uri}
  AddTags(resource_id, region, **tags)


@vm_util.Retry()
def IssueRetryableCommand(cmd, env=None):
  """Tries running the provided command until it succeeds or times out.

  Args:
    cmd: A list of strings such as is given to the subprocess.Popen()
        constructor.
    env: An alternate environment to pass to the Popen command.

  Returns:
    A tuple of stdout and stderr from running the provided command.
  """
  stdout, stderr, retcode = vm_util.IssueCommand(cmd, env=env)
  if retcode:
    raise errors.VmUtil.CalledProcessException(
        'Command returned a non-zero exit code.\n')
  if stderr:
    raise errors.VmUtil.CalledProcessException(
        'The command had output on stderr:\n%s' % stderr)
  return stdout, stderr
