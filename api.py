import os
import time
import paramiko
import router
import boto

def cmd(userid=None, passwd=None, action=None):
    print "Initial User Command"
    ec2 = boto.connect_ec2(aws_access_key_id=userid, aws_secret_access_key=passwd)
    print ec2
    print "done"

