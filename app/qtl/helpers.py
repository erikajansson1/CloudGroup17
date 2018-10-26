# http://docs.openstack.org/developer/python-novaclient/ref/v2/servers.html
import time, os, sys
import inspect
from os import environ as env

from ..auth.helpers import generate_token
from ..auth.models import User
from .models import Cluster, VirtualMachine
from .. import db
import requests

from  novaclient import client
import keystoneclient.v3.client as ksclient
from keystoneauth1 import loading
from keystoneauth1 import session
import json

loader = loading.get_plugin_loader('password')

auth = loader.load_from_options(auth_url=env['OS_AUTH_URL'],
	                        username=env['OS_USERNAME'],
	                        password=env['OS_PASSWORD'],
	                        project_name=env['OS_PROJECT_NAME'],
	                        project_domain_name=env['OS_USER_DOMAIN_NAME'],
	                        project_id=env['OS_PROJECT_ID'],
	                        user_domain_name=env['OS_USER_DOMAIN_NAME'])

sess = session.Session(auth=auth)
nova = client.Client('2.1', session=sess)
print "user authorization completed."

def delete_instance_by_id(instance_id):
	try:
		instance = nova.servers.get(instance_id)
		nova.servers.delete(instance)
	except Exception as e:
		print e.message
		return json.dumps({"success": False, "message": e.message})

	return json.dumps({"success": True})

def delete_instance(vm):
	print "delete instance id: " + vm.id
	db.session.delete(vm)
	db.session.commit()
	
	try:
		instance = nova.servers.get(vm.id)
		nova.servers.delete(instance)
	except Exception as e:
		return json.dumps({"success": False, "message": e.message})

	return json.dumps({"success": True})

def delete_instances_by_id(instance_ids):
	for instance_id in instance_ids:
		delete_instance_by_id(instance_id)

	return json.dumps({"success": True})

def delete_instances(vms):
	for vm in vms:
		delete_instance(vm)

	return json.dumps({"success": True})

def delete_cluster(user_id, cluster_id):
	print "Delete cluster"
	cluster = Cluster.query.filter_by(id=cluster_id, user_id=user_id).first()
	if cluster is not None:
		print cluster
		delete_instances(cluster.vms)

		db.session.delete(cluster)
		db.session.commit()
		return json.dumps({"success": True})
	else:
		return json.dumps({"success": False, "message": "Cannot find cluster"})

def create_ansible():
	flavor = "ACCHT18.large" 
	private_net = "SNIC 2018/10-30 Internal IPv4 Network"
	floating_ip_pool_name = "Public External IPv4 network"
	image_name = "Ubuntu 16.04 LTS (Xenial Xerus) - latest"
	keypair_name = "keypairc1"

	image = nova.glance.find_image(image_name)

	flavor = nova.flavors.find(name=flavor)
	
	try:
		nova.floating_ip_pools.list()
		floating_ip = nova.floating_ips.create(nova.floating_ip_pools.list()[0].name)
	except Exception as e:
		return json.dumps({"success": False, 'message': e.message})

	if private_net != None:
	    net = nova.neutron.find_network(private_net)
	    nics = [{'net-id': net.id}]
	else:
		return json.dumps({"success": False, 'message': "private-net not defined."})

	#print("Path at terminal when executing this file")
	#print(os.getcwd() + "\n")
	cfg_file_path =  os.getcwd()+'/app/qtl/ansible_cloud-cfg.txt'
	if os.path.isfile(cfg_file_path):
	    userdata = open(cfg_file_path)
	else:
		return json.dumps({"success": False, 'message': 'Cannot find ansible_cloud-cfg.txt'})

	secgroups = ['default', 'hungphan_security_c1']

	print "Creating instance ... "
	instance = nova.servers.create(name='ACC17_ANSIBLE_IMPORTANT', 
					image=image, 
					flavor=flavor, 
					userdata=userdata, 
					nics=nics,
					security_groups=secgroups,
					key_name = keypair_name)


	inst_status = instance.status

	print "waiting for 10 seconds.. "
	time.sleep(10)

	while inst_status == 'BUILD':
	    print "Instance: "+instance.name+" is in "+inst_status+" state, sleeping for 5 seconds more..."
	    time.sleep(5)
	    instance = nova.servers.get(instance.id)
	    inst_status = instance.status

	#add floating IP to instane
	instance.add_floating_ip(floating_ip)

	return json.dumps({'success': True,
						'id': instance.id,
						'name': instance.name,
						'floating_ip': floating_ip.ip,
						'private_ip': instance.networks[private_net][0],
						'status': inst_status
	})

def create_master():
	flavor = "ACCHT18.large" 
	private_net = "SNIC 2018/10-30 Internal IPv4 Network"
	floating_ip_pool_name = "Public External IPv4 network"
	image_name = "Ubuntu 16.04 LTS (Xenial Xerus) - latest"

	image = nova.glance.find_image(image_name)

	flavor = nova.flavors.find(name=flavor)
	
	try:
		nova.floating_ip_pools.list()
		floating_ip = nova.floating_ips.create(nova.floating_ip_pools.list()[0].name)
	except Exception as e:
		return json.dumps({"success": False, 'message': e.message})

	if private_net != None:
	    net = nova.neutron.find_network(private_net)
	    nics = [{'net-id': net.id}]
	else:
		return json.dumps({"success": False, 'message': "private-net not defined."})

	#print("Path at terminal when executing this file")
	#print(os.getcwd() + "\n")
	cfg_file_path =  os.getcwd()+'/app/qtl/master_cloud-cfg.txt'
	if os.path.isfile(cfg_file_path):
	    userdata = open(cfg_file_path)
	else:
		return json.dumps({"success": False, 'message': 'Cannot find master_cloud-cfg.txt'})

	secgroups = ['default', 'hungphan_security_c1']

	print "Creating instance ... "
	instance = nova.servers.create(name='ACC17_MASTER_IMPORTANT', 
					image=image, 
					flavor=flavor, 
					userdata=userdata, 
					nics=nics,
					security_groups=secgroups)


	inst_status = instance.status

	print "waiting for 10 seconds.. "
	time.sleep(10)

	while inst_status == 'BUILD':
	    print "Instance: "+instance.name+" is in "+inst_status+" state, sleeping for 5 seconds more..."
	    time.sleep(5)
	    instance = nova.servers.get(instance.id)
	    inst_status = instance.status

	#add floating IP to instane
	instance.add_floating_ip(floating_ip)

	return json.dumps({'success': True,
						'id': instance.id,
						'name': instance.name,
						'floating_ip': floating_ip.ip,
						'private_ip': instance.networks[private_net][0],
						'status': inst_status
	})

def create_worker():
	flavor = "ACCHT18.large" 
	private_net = "SNIC 2018/10-30 Internal IPv4 Network"
	floating_ip_pool_name = "Public External IPv4 network"
	image_name = "Ubuntu 16.04 LTS (Xenial Xerus) - latest"

	image = nova.glance.find_image(image_name)

	flavor = nova.flavors.find(name=flavor)
	
	if private_net != None:
	    net = nova.neutron.find_network(private_net)
	    nics = [{'net-id': net.id}]
	else:
		return json.dumps({"success": False, 'message': "private-net not defined."})

	#print("Path at terminal when executing this file")
	#print(os.getcwd() + "\n")
	cfg_file_path =  os.getcwd()+'/app/qtl/worker_cloud-cfg.txt'
	if os.path.isfile(cfg_file_path):
	    userdata = open(cfg_file_path)
	else:
		return json.dumps({"success": False, 'message': 'Cannot find worker_cloud-cfg.txt'})

	secgroups = ['default', 'hungphan_security_c1']

	print "Creating instance ... "
	instance = nova.servers.create(name='ACC17_WORKER_IMPORTANT', 
					image=image, 
					flavor=flavor, 
					userdata=userdata, 
					nics=nics,
					security_groups=secgroups)


	inst_status = instance.status

	print "waiting for 10 seconds.. "
	time.sleep(10)

	while inst_status == 'BUILD':
	    print "Instance: "+instance.name+" is in "+inst_status+" state, sleeping for 5 seconds more..."
	    time.sleep(5)
	    instance = nova.servers.get(instance.id)
	    inst_status = instance.status

	return json.dumps({'success': True,
						'id': instance.id,
						'name': instance.name,
						'floating_ip': None,
						'private_ip': instance.networks[private_net][0],
						'status': inst_status
	})

def create_cluster(user_id, number_of_workers):
	user = User.query.filter_by(id=user_id).first()
	vm_ids = []
	
	#Start VM with openstackclient
	try:
		ansible_json = create_ansible()
		print ansible_json
		vm_ids.append(json.loads(ansible_json)['id'])

		master_json = create_master()
		print master_json
		vm_ids.append(json.loads(master_json)['id'])

		worker_jsons = json.loads("[]")
		for i in range(int(number_of_workers)):
			worker_json = create_worker()
			print worker_json
			vm_ids.append(json.loads(worker_json)['id'])
			worker_jsons.append(worker_json)

	#Delete all new created VM if any trouble occurs
	except Exception as e:
		delete_instances_by_id(vm_ids)
		return json.dumps({"success": False, "message": "Cannot start VMs"})

	for i in range(10) :
		time.sleep(30)
		#call API
		headers = {'Authorization': generate_token(user_id)}
		data = {'ansible_ip': json.loads(ansible_json)['private_ip'], 
				'master_ip': json.loads(master_json)['private_ip'],
		 		'worker_ip': []}

		for worker_json in worker_jsons:
			data['worker_ip'].append(json.loads(worker_json)['private_ip'])
		
		try:
			res = requests.post('http://' + json.loads(ansible_json)['floating_ip'] + ":5000/install", headers=headers, data=data)
			if not res.json()['success']:
				delete_instances_by_id(vm_ids)
				return json.dumps({"success": False, "message": "Ansible Node cannot install"})
			break
		except:
			continue
	
	response_data = {}

	#Ansible is not ready after 4 minutes
	if i == 9:
		delete_instances_by_id(vm_ids)
		return json.dumps({"success": False, "message": "Ansible Node cannot install"})
	else:
		#Ask sparkmaster for jupyter token
		for j in range(6):
			try:
				headers = {'Authorization': generate_token(user_id)}
				res = requests.post('http://' + json.loads(master_json)['floating_ip'] + ":5000/jupyter/token", headers=headers, data=data)
				response_data['jupyter_url'] = json.loads(master_json)['floating_ip'] + ":" + str(res.json()['port']) + "/?token=" + res.json()['token']
				response_data['success'] = True
				break
			except:
				time.sleep(5)
				continue
			
		if j == 5:
			delete_instances_by_id(vm_ids)
			return json.dumps({"success": False, "message": "Spark Master is Down"})

		#Update database
		#Create VM
		vms = []
		vms.append(VirtualMachine(id=json.loads(ansible_json)['id'], vm_type=VirtualMachine.ANSIBLE, public_ip=json.loads(ansible_json)['floating_ip'], private_ip=json.loads(ansible_json)['private_ip']))
		vms.append(VirtualMachine(id=json.loads(master_json)['id'], vm_type=VirtualMachine.SPARK_MASTER, public_ip=json.loads(master_json)['floating_ip'], private_ip=json.loads(master_json)['private_ip']))
		
		for worker_json in worker_jsons:
			vms.append(VirtualMachine(id=json.loads(worker_json)['id'], vm_type=VirtualMachine.SPARK_WORKER, public_ip=None, private_ip=json.loads(worker_json)['private_ip']))
		
		#Create Cluster
		cluster = Cluster(vms=vms, jupyter_url=response_data['jupyter_url'])

		user.clusters.append(cluster)
		db.session.commit()

		ansible_vm = master_vm = VirtualMachine.query.filter_by(id=json.loads(ansible_json)['id']).first()
		response_data['cluster_id'] = ansible_vm.cluster_id
	
	return json.dumps(response_data)

def scale_worker(user_id, cluster_id, number_of_workers):
	cluster = Cluster.query.filter_by(id=cluster_id, user_id=user_id).first()

	if cluster is None:
		return json.dumps({"success": False, "message": "Cannot find cluster"})

	vms = cluster.vms
	master_vm = VirtualMachine.query.filter_by(cluster_id=cluster_id, vm_type=VirtualMachine.SPARK_MASTER).first()
	ansible_vm = VirtualMachine.query.filter_by(cluster_id=cluster_id, vm_type=VirtualMachine.ANSIBLE).first()
	
	diff = (len(vms) - 2) - int(number_of_workers)

	if diff < 0:
		#Increase
		vm_ids = []
		worker_jsons = json.loads("[]")
		try:
			for i in range(-diff):
				worker_json = create_worker()
				print worker_json
				vm_ids.append(json.loads(worker_json)['id'])
				worker_jsons.append(worker_json)
	
		#Delete all new created VM if any trouble occurs
		except Exception as e:
			print e.message
			delete_instances_by_id(vm_ids)
			return json.dumps({"success": False, "message": "Cannot start VMs"})


		#call API to ANSIBLE to start installing
		headers = {'Authorization': generate_token(user_id)}
		data = {'ansible_ip': ansible_vm.private_ip, 
				'master_ip': master_vm.private_ip,
		 		'worker_ip': []}

		for worker_json in worker_jsons:
			data['worker_ip'].append(json.loads(worker_json)['private_ip'])
		
		for vm in vms:
			if vm.vm_type == VirtualMachine.SPARK_WORKER:
				data['worker_ip'].append(vm.private_ip)
		
		try:
			res = requests.post('http://' + ansible_vm.public_ip + ":5000/install", headers=headers, data=data)
			print res.json()
			if not res.json()['success']:
				delete_instances_by_id(vm_ids)
				return json.dumps({"success": False, "message": "Ansible Node cannot install"})
		except:
				delete_instances_by_id(vm_ids)
				return json.dumps({"success": False, "message": "Ansible Node cannot install"})
		
		#Update database
		for worker_json in worker_jsons:
			vms.append(VirtualMachine(id=json.loads(worker_json)['id'], vm_type=VirtualMachine.SPARK_WORKER, public_ip=None, private_ip=json.loads(worker_json)['private_ip']))
		db.session.commit()



	elif diff > 0:
		for i in range(diff):
			delete_instance(vms[i])
		#decrease

	return json.dumps({"success": True})