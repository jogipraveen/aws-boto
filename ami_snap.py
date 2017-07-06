#!/usr/bin/env python
"""
This script is used to create an AMI for the list1 and keep latest two AMIs and delete remaining of them
"""
import sys
import boto
import boto.ec2
import re
import datetime
import time

list_1 = ['<instance1-name>','<instance2-name>','<instance3-name>']   #instances to create AMI
conn = boto.ec2.connect_to_region('us-west-1')

def create_img(a, b):
    try:
        img_id = conn.create_image(a, b, description='backup', no_reboot=True, dry_run=False)
    except boto.exception.BotoServerError, e:
        print e.error_message
    return(img_id)

def delete_img(c):
    try:
        c_name = re.sub(r'-[0-9]*$',"", c)
        list_images = conn.get_all_images(filters={'owner_id':'<owner_id>'})
        list_2 = dict()
        for i in list_images:
            m = re.sub(r'-[0-9]*$',"", i.name)
            if m == c_name: 
                list_2[i.id] = i.creationDate
        if len(list_2) > 2 :
            values = sorted(list_2.values())
            for k, v in list_2.iteritems():
                if v == values[0]:
                    print "Delete the following AMI id : %s" % k
                    print "------------------------------------------"
                    conn.deregister_image(k, delete_snapshot=True, dry_run=False)
                    time.sleep(60) #wait until delete the snapshot associated with an EBS volume mounted at /dev/sda1
                    delete_snap(k)
        else:
            print "All AMI snaps are up to date"
            print "----------------------------"
    except boto.exception.BotoServerError, e:
        print e.error_message

def delete_snap(b):
    try:
        list_snaps = conn.get_all_snapshots(filters={'owner_id' :'<owner_id>'})
        for i in list_snaps:
            find_ami_id = re.search(r'.* for (.*) from .*', i.description, re.M|re.I)
            if find_ami_id:
                if find_ami_id.group(1) == b:
                    conn.delete_snapshot(i.id, dry_run=False)
                    time.sleep(30) #wait for a while to delete snapshots one by one
    except boto.exception.BotoServerError, e:
        print e.error_message

def main():
    reservations = conn.get_all_instances()
    for res in reservations:
        for inst in res.instances:
            if 'Name' in inst.tags and inst.tags['Name'] in list_1:
                print "%s (%s) [%s]" % (inst.tags['Name'], inst.id, inst.state)
                name = inst.tags['Name'] + '-' + datetime.datetime.now().strftime("%Y%m%d%H%M")
                print "Starting AMI creation for : %s" % inst.tags['Name']
                ami_id = create_img(inst.id, name)
                img = conn.get_all_images(filters={'image_id' : ami_id})[0]
            
                if img.state == 'failed':
                    print "AMI creation failed for instance: %s (AMI id: %s)" % (inst.tags['Name'],ami_id)
                elif img.state == 'pending':
                    while True:
                        if img.state == 'failed':
                            print "AMI creation failed for instance: %s (AMI id: %s)" % (inst.tags['Name'],ami_id)
                            break                        
                        elif img.state == 'available':
                            print "AMI creation completed for instance: %s (AMI id: %s)" % (inst.tags['Name'],ami_id)
                            print "Checking for old AMIs (instance:- %s)" % inst.tags['Name']
                            time.sleep(180) # wait for while to update instance to the list
                            delete_img(name)
                            break
                        else:
                            time.sleep(10)
                            img = conn.get_all_images(filters={'image_id' : ami_id})[0]
                elif img.state == 'available':
                    print "AMI creation completed for instance: %s (AMI id: %s)" % (inst.tags['Name'],ami_id)
                    print "Checking for old AMIs (instance:- %s)" % inst.tags['Name']
                    time.sleep(180) # wait for while to update instance to the list
                    delete_img(name)
                else:
                    print "Couldn't find the AMI" 

if __name__ == "__main__":
    main()
