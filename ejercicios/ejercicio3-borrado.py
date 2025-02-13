from common import aws_resource_functions as aws
import boto3

# Nombres de las instancias y grupos de seguridad
nombres_instancias = ['frontend-1', 'frontend-2', 'backend', 'balanceador', 'nfs']
nombres_sg = ['frontend-sg', 'frontend-sg', 'backend-sg', 'balanceador-sg', 'nfs-sg']

# Eliminar las instancias y liberar IPs elásticas
for nombre_instancia in nombres_instancias:
    id_instancia = aws.get_instance_id(nombre_instancia)
    if id_instancia:
        aws.terminate_instance(id_instancia)
        aws.release_elastic_ip(id_instancia)

# Eliminar grupos de seguridad
for nombre_sg in set(nombres_sg):
    aws.delete_security_group(nombre_sg)