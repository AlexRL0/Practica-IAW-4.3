from common import aws_resource_functions as aws
import boto3
import time

# Nombres de las instancias y grupos de seguridad
nombres_instancias = ['frontend-1', 'frontend-2', 'backend', 'balanceador', 'nfs']
nombres_sg = ['frontend-sg', 'frontend-sg', 'backend-sg', 'balanceador-sg', 'nfs-sg']

# Desvincular y liberar IPs elásticas
for nombre_instancia in nombres_instancias:
    id_instancia = aws.get_instance_id(nombre_instancia)
    if id_instancia:
        public_ip = aws.get_instance_public_ip(id_instancia)
        if public_ip:
            aws.disassociate_elastic_ip(public_ip)
            aws.release_elastic_ip(public_ip)

# Terminar instancias
for nombre_instancia in nombres_instancias:
    id_instancia = aws.get_instance_id(nombre_instancia)
    if id_instancia:
        aws.terminate_instance_by_id(id_instancia)

# Esperar hasta que todas las instancias sean terminadas
ec2 = boto3.resource('ec2')
for nombre_instancia in nombres_instancias:
    id_instancia = aws.get_instance_id(nombre_instancia)
    if id_instancia:
        instance = ec2.Instance(id_instancia)
        instance.wait_until_terminated()
        
# Eliminar grupos de seguridad
for nombre_sg in nombres_sg:
    if aws.security_group_exists(nombre_sg):
        aws.delete_security_group(nombre_sg)
