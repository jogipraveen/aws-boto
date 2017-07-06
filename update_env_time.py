#!/usr/bin/env python
""" 
script is used to update instance tags 
"""
import sys
import boto
import boto.ec2

def main():
    conn = boto.ec2.connect_to_region('us-west-1')
    reservations = conn.get_all_instances()
    for res in reservations:
        for inst in res.instances:
	    if 'Name' in inst.tags:
	        if sys.argv[1] in inst.tags['Name']:
		    try:
		        conn.delete_tags([inst.id], {'ExpirationDate': inst.tags['ExpirationDate']})
                    except boto.exception.BotoServerError, e:
                        print e.error_message
                    try:
                        conn.create_tags([inst.id], {'ExpirationDate': sys.argv[2]})
                    except boto.exception.BotoServerError, e:
                        print e.error_message

if __name__ == "__main__":
    main()
