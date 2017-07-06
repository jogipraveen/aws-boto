#!/usr/bin/env python
""" 
Delete volumes which are not associated with any instance
"""
import boto
import boto.ec2

conn_ec2 = boto.ec2.connect_to_region('us-west-1')

def main():
    volumes = conn_ec2.get_all_volumes(filters={'status' : 'available', 'size' : '8'})
    print "Delete the following Volumes"
    for i in volumes:
        try:
            print "Volume:%s size:%s status:%s" %(i.id,i.size,i.status)
            conn_ec2.delete_volume(i.id, dry_run=False)
        except boto.exception.BotoServerError, e:
	    print e.error_message

if __name__ == "__main__":
    main()
