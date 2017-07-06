#!/usr/bin/env python
"""
This script is used to check if an instance is an Ephemeral instance
"""
import boto
import boto.ec2
import sys

conn = boto.ec2.connect_to_region('us-west-1')
reservations = conn.get_all_instances(filters={"tag:Ephemeral": "yes"})
instances = []

for r in reservations:
    for i in r.instances:
        if i.state == 'running':
	    instances.append(i.tags['Name'])

if sys.argv[1] not in instances:
    print(1)
