from . import auth
from .. import db
from app.auth.models import User
from app.qtl.models import Cluster, VirtualMachine

# @auth.route('/')
# def say_hello():
#     user = User(username='admin', email="hnphan@gmail.com", password='admin@example.com')
#     vm1 = VirtualMachine(name='vm1', vm_type='Ansible Master', public_ip='0.0.0.0', private_ip='192.168.1.1')
#     vm2 = VirtualMachine(name='vm2', vm_type='Spark Master', public_ip='0.0.0.1', private_ip='192.168.1.2')
#     vm3 = VirtualMachine(name='vm3', vm_type='Spark Worker', public_ip='0.0.0.2', private_ip='192.168.1.3')

#     cluster = Cluster(jupyter_url='xxx')
#     cluster.vms.append(vm1)
#     cluster.vms.append(vm2)
#     cluster.vms.append(vm3)
#     user.clusters.append(cluster)
    

#     db.session.add(user)
#     db.session.commit()


#     return "Hello"


# @auth.route("/status")
# def get_status():
#     user = User.query.filter_by(username='admin').first()
#     if user is not None:
#         for cluster in user.clusters:
#             for vm in cluster.vms:
#                 print str(vm.id) + "\t" + vm.name + "\t" + vm.private_ip + "\n"

#     return "OK"

# @auth.route("/user/delete")
# def delete_user():
#     user = User.query.filter_by(username='admin').first()
#     if user is not None:
#         db.session.delete(user)
#         db.session.commit()

#     return "OK"


# @auth.route("/delete")
# def delete_vm():
#     vm = VirtualMachine.query.filter_by(name="vm1").first()
#     print str(vm)
#     print vm.name + "\t" + vm.private_ip + "\n"
    
#     if vm is None:
#         print "NONE\n"
#     else:
#         db.session.delete(vm)
#         db.session.commit()

#     return "OK"


    

