#!/usr/bin/python
"""
script is used to delete dummy DNS entries on route53(if the environment was deleted already)
"""

import re
import boto
import boto.ec2
import boto.route53.connection

conn_ec2 = boto.ec2.connect_to_region('us-west-1')
conn_rt53 = boto.route53.connection.Route53Connection()
zone_rt53 = conn_rt53.get_zone('<domain_name.com>')

def list_instances():
    reservations = conn_ec2.get_all_instances(filters={"tag:Ephemeral": "yes"})
    instances = []
    for r in reservations:
        for i in r.instances:
            instances.append(i)
    return(instances)

def del_DNS_record(name):
    change_set = boto.route53.record.ResourceRecordSets(conn_rt53, zone_rt53.id)
    u = change_set.add_change("DELETE", name+".<domain_name.com>", "A")
    u.add_value("0.0.0.0")
    results = change_set.commit()

def main():
    rec = zone_rt53.get_records() #Get all records in <domain_name.com>
    for i in rec:
        j = str(i)
        """
        Apply some regular expressions to get the Ephemeral environment tag
        """
	pattern = re.compile("<Record:ephemeral*")
        match = pattern.match(j)
        if match:
            cut_1 = re.sub(r'<Record:',"", j)
            cut_2 = re.sub(r'.*:A:',"", cut_1)
            ip = re.sub(r'>',"", cut_2)
            if ip == '0.0.0.0': #Compare ip of the Ephemeral environment
                """
                Ephemeral environment tag for eg:ephemerale91474cbb471ab4d58eb5da6e02aa70ab44f6897-10558
                """
                tag_1 = re.sub(r'.<domain_name.com>.:A:0.0.0.0>',"", cut_1) 
                instances = list_instances()
                """
                Check Ephemeral environment is exists
                """
                if tag_1 not in instances: 
                    print "Trying to delete environment tag :%s - ip: %s" %(tag_1,ip)
                    """ Delete DNS record """
                    del_DNS_record(tag_1) 
if __name__ == "__main__":
    main()
