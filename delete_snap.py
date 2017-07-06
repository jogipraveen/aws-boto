#!/usr/bin/env python
"""
Delete Snapshots if there aree no corresponding AMIs were found
"""
import boto
import boto.ec2
import datetime
import operator
import re

conn = boto.ec2.connect_to_region('us-west-1')

def days_between(d1,d2):
    d1 = datetime.datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)

def main():
    try:
        snaps = conn.get_all_snapshots(filters={'owner_id' :'<owner_id>','status': 'completed'})
        volumes = conn.get_all_volumes()
        images = conn.get_all_images(filters={'owner_id':'<owner_id>'})
        instances = conn.get_all_instances()
        
        """ list of volumes """   
        list_1 = list() 
        """ list of images(ami) """
        list_2 = list() 
        """ list of instances """
        list_3 = list() 
        """ dictonary of snap_id and date """
        dict_1 = dict() 

        for x in volumes:
            list_1.append(x.id) 
        for y in images:
            list_2.append(y.id)
        for z in instances:
            list_3.append(z.id)
        for i in snaps:
            if i.volume_id not in list_1:
                ami = re.search(r'.* for (.*) from .*', i.description, re.M|re.I)
                instance = re.search(r'.* CreateImage((.*)) for .*', i.description, re.M|re.I)
                if ami and instance:
                    ami_id = ami.group(1)
                    instance_id = instance.group(1).strip('()') 
                    snap_date = datetime.datetime.strptime(i.start_time, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')
                    format = "%Y-%m-%d"
                    today = datetime.datetime.today()
                    sys_date = today.strftime(format)
                    days = days_between(sys_date,snap_date)
                    if ami_id not in list_2 and instance_id not in list_3 and days > 30:
                        dict_1[i.id] = i.start_time
        sorted_dict_1 = sorted(dict_1.items(), key=operator.itemgetter(1))
        for k, v in sorted_dict_1:
            print "Delete the following snap id: %s and date of creation: %s" %(k,v)
            try:
                conn.delete_snapshot(k, dry_run=False)
            except boto.exception.BotoServerError, e:
                print e.error_message

    except boto.exception.BotoServerError, e:
        print e.error_message

if __name__ == "__main__":
    main()
