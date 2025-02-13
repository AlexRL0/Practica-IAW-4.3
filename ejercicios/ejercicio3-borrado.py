import boto3
import botocore
from common import aws_resource_functions as aws

# Obtener todas las IPs elásticas y sus instancias asociadas
def get_elastic_ips():
    ec2 = boto3.client('ec2')
    addresses = ec2.describe_addresses()
    elastic_ips = {}
    for address in addresses['Addresses']:
        if 'InstanceId' in address:
            elastic_ips[address['InstanceId']] = address['PublicIp']
    return elastic_ips

# Nombres de las instancias y grupos de seguridad
nombres_instancias = ['frontend-1', 'frontend-2', 'backend', 'balanceador', 'nfs']
nombres_sg = ['frontend-sg', 'frontend-sg', 'backend-sg', 'balanceador-sg', 'nfs-sg']

# Obtener IPs elásticas asignadas a cada instancia
ips_elasticas = get_elastic_ips()

# Disociar y liberar IPs elásticas
for instance_id, ip_elastica in ips_elasticas.items():
    try:
        aws.disassociate_elastic_ip(ip_elastica)
        aws.release_elastic_ip(ip_elastica)
    except Exception as e:
        print(f'Ocurrió un error al disociar/liberar IP {ip_elastica} para la instancia {instance_id}: {e}')

# Terminar instancias
for nombre_instancia in nombres_instancias:
    try:
        instance_id = aws.get_instance_id(nombre_instancia)
        if instance_id:
            aws.terminate_instance_by_id(instance_id)
        else:
            print(f'No se encontró la instancia {nombre_instancia}.')
    except Exception as e:
        print(f'Ocurrió un error al terminar la instancia {nombre_instancia}: {e}')

# Eliminar grupos de seguridad
for nombre_sg in set(nombres_sg):  # Usamos set para evitar duplicados
    try:
        aws.delete_security_group(nombre_sg)
    except Exception as e:
        print(f'Ocurrió un error al eliminar el grupo de seguridad {nombre_sg}: {e}')