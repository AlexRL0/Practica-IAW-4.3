from common import aws_resource_functions as aws
import time

# Nombres de las instancias y grupos de seguridad
nombres_instancias = ['frontend-1', 'frontend-2', 'backend', 'balanceador', 'nfs']
nombres_sg = ['frontend-sg', 'backend-sg', 'balanceador-sg', 'nfs-sg']

# Eliminar las instancias, liberar IPs elásticas y eliminar grupos de seguridad
for nombre_instancia in nombres_instancias:
    id_instancia = aws.get_instance_id(nombre_instancia)
    if id_instancia:
        ip_elastica = aws.get_instance_public_ip(id_instancia)
        if ip_elastica:
            try:
                aws.disassociate_elastic_ip(ip_elastica)
                aws.release_elastic_ip(ip_elastica)
            except Exception as e:
                print(f'Error al desasociar o liberar IP elástica {ip_elastica} para la instancia {id_instancia}: {e}')
        aws.terminate_instance_by_id(id_instancia)
    else:
        print(f'Instancia {nombre_instancia} no encontrada o ya terminada')

# Esperar un tiempo para asegurar que las instancias y IPs sean liberadas
time.sleep(60)

# Eliminar grupos de seguridad y manejar dependencias
for nombre_sg in nombres_sg:
    if aws.security_group_exists(nombre_sg):
        group_id = aws.get_security_group_id(nombre_sg)
        if group_id:
            try:
                # Desasociar el grupo de seguridad de las interfaces de red
                ec2 = boto3.resource('ec2')
                interfaces = ec2.describe_network_interfaces(Filters=[{'Name': 'group-id', 'Values': [group_id]}])
                for interface in interfaces['NetworkInterfaces']:
                    ec2.modify_network_interface_attribute(NetworkInterfaceId=interface['NetworkInterfaceId'], Groups=[])
                    print(f'Interface {interface["NetworkInterfaceId"]} desasociada del grupo de seguridad {group_id}')
                # Eliminar el grupo de seguridad
                aws.delete_security_group(nombre_sg)
            except Exception as e:
                print(f'Error al eliminar el grupo de seguridad {nombre_sg}: {e}')
    else:
        print(f'El grupo de seguridad {nombre_sg} no se encontró o ya fue eliminado')