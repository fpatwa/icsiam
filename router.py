
import os
import time
import boto
import boto.manage.cmdshell
import paramiko
# ami-70f96e40
#ami='ami-7341831a',
# ec2.get_all_images(filters={'name':'*ubuntu'})

def find_images():
    ec2 = boto.connect_ec2()
    image_list = ec2.get_all_images(filters={'name':'*ubuntu'})
    print image_list

def launch_instance(ami='ami-7341831a',
		    instance_type='t1.micro',
		    key_name='paws',
		    key_extension='.pem',
		    key_dir='~/.ssh',
		    group_name='paws',
		    ssh_port=22,
		    cidr='0.0.0.0/0',
		    tag='paws',
		    user_data=None,
		    cmd_shell=True,
		    login_user='ec2-user',
		    ssh_passwd=None):

  
    """
    Launch and instance and wait for it to start running.
    Returns a tuple consisting of the INstamce object and the CmdShell
    object, if request, or None.
    """

    cmd = None

    ec2 = boto.connect_ec2()

    try:
	key = ec2.get_all_key_pairs(keynames=[key_name])[0]
    except ec2.ResponseError, e:
	if e.code == 'InvalidKeyPair.NotFound':
	    print 'Creating keypair: %s' % key_name
	    
	    key = ec2.create_key_pair(key_name)

	    key.save(key_dir)
	else:
	    raise

    try:
	group = ec2.get_all_security_groups(groupnames=[group_name])[0]
    except ec2.ResponseError, e:
	if e.code == 'InvalidGroup.NotFound':
	    print 'Creating Security Group: %s' % group_name
	    # Create a security group to control access to instance via SSH.
	    group = ec2.create_security_group(group_name,
					      'A group that allows SSH access')
	else:
	    raise

    try:
	group.authorize('tcp', ssh_port, ssh_port, cidr)
    except ec2.ResponseError, e:
	if e.code == 'InvalidPermission.Duplicate':
	    print 'Security Group: %s already authorized' % group_name
	else:
	    raise

    reservation = ec2.run_instances(ami,
				    key_name=key_name,
				    security_groups=[group_name],
				    instance_type=instance_type,
				    user_data=user_data)

    instance = reservation.instances[0]

    print 'waiting for instance'
    while instance.state != 'running':
	print '.'
	time.sleep(5)
	instance.update()
    print 'done'

    instance.add_tag(tag)

    if cmd_shell:
	print "Before Khalid"
	key_path = os.path.join(os.path.expanduser(key_dir),
				key_name+key_extension)
	print "Just for Khalid"
        print key_path
	cmd = boto.manage.cmdshell.sshclient_from_instance(instance,
							   key_path,
							   user_name=login_user)

    return (instance, cmd)		

def connect_to_instance(instance_id="i-84b30ee0",
			username="ec2-user",
			key_dir="/home/stack/.ssh",
			key_extension=".pem"):

    ec2 = boto.connect_ec2()

    instance = ec2.get_all_instances(instance_ids=instance_id)[0].instances[0]
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    key_path = key_dir + '/' + instance.key_name + key_extension
    ssh.connect(instance.public_dns_name, username=username, key_filename=key_path)

    stdin, stdout, stderr = ssh.exec_command("uptime;ls -l;touch mickymouse;ls -l;uptime;rm -f mickymouse")
    stdin.flush()
    data = stdout.read().splitlines()
    for line in data:
        print line
    ssh.close()
