from common import aws_resource_functions as aws

# Nombres de las instancias y grupos de seguridad
nombres_instancias = ['frontend-1', 'frontend-2', 'backend', 'balanceador', 'nfs']
nombres_sg = ['frontend-sg', 'backend-sg', 'balanceador-sg', 'nfs-sg']

# Eliminar las instancias, liberar IPs elásticas y eliminar grupos de seguridad
for nombre_instancia in nombres_instancias:
    id_instancia = aws.get_instance_id(nombre_instancia)
    if id_instancia:
        ip_elastica = aws.get_instance_public_ip(id_instancia)
        aws.disassociate_elastic_ip(ip_elastica)
        aws.release_elastic_ip(ip_elastica)
        aws.terminate_instance_by_id(id_instancia)
    else:
        print(f'Instancia {nombre_instancia} no encontrada o ya terminada')

# Eliminar grupos de seguridad
for nombre_sg in nombres_sg:
    if aws.security_group_exists(nombre_sg):
        aws.delete_security_group(nombre_sg)
    else:
        print(f'El grupo de seguridad {nombre_sg} no se encontró o ya fue eliminado')