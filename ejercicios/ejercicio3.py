from common import aws_resource_functions as aws
import time

# ID del AMI
ami = 'ami-04b4f1a9cf54c11d0'

# Tipo de instancia
instance_type = 't2.micro'

# Clave privada
key_name = 'vockey'

# Nombres de las instancias y grupos de seguridad
nombres_instancias = ['frontend-1', 'frontend-2', 'backend', 'balanceador', 'nfs']
nombres_sg = ['frontend-sg', 'frontend-sg', 'backend-sg', 'balanceador-sg', 'nfs-sg']

# Reglas para los grupos de seguridad
reglas_sg = {
    'frontend-sg': [
        {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'CidrIp': '0.0.0.0/0'},
        {'IpProtocol': 'tcp', 'FromPort': 2049, 'ToPort': 2049, 'CidrIp': '0.0.0.0/0'},
        {'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80, 'CidrIp': '0.0.0.0/0'},
        {'IpProtocol': 'tcp', 'FromPort': 443, 'ToPort': 443, 'CidrIp': '0.0.0.0/0'},
        {'IpProtocol': 'tcp', 'FromPort': 3306, 'ToPort': 3306, 'CidrIp': '0.0.0.0/0'}
    ],
    'backend-sg': [
        {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'CidrIp': '0.0.0.0/0'},
        {'IpProtocol': 'tcp', 'FromPort': 3306, 'ToPort': 3306, 'CidrIp': '0.0.0.0/0'}
    ],
    'balanceador-sg': [
        {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'CidrIp': '0.0.0.0/0'},
        {'IpProtocol': 'tcp', 'FromPort': 3306, 'ToPort': 3306, 'CidrIp': '0.0.0.0/0'},
        {'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80, 'CidrIp': '0.0.0.0/0'},
        {'IpProtocol': 'tcp', 'FromPort': 443, 'ToPort': 443, 'CidrIp': '0.0.0.0/0'},
        {'IpProtocol': 'tcp', 'FromPort': 2049, 'ToPort': 2049, 'CidrIp': '0.0.0.0/0'}
    ],
    'nfs-sg': [
        {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'CidrIp': '0.0.0.0/0'},
        {'IpProtocol': 'tcp', 'FromPort': 2049, 'ToPort': 2049, 'CidrIp': '0.0.0.0/0'}
    ]
}

# Crear grupos de seguridad si no existen
for nombre_sg, reglas in reglas_sg.items():
    if not aws.security_group_exists(nombre_sg):
        aws.create_security_group(nombre_sg, f'Reglas para {nombre_sg}', reglas)

# Crear IPs elásticas
ips_elasticas = {}
for nombre_instancia in nombres_instancias:
    ip_elastica = aws.allocate_elastic_ip()
    ips_elasticas[nombre_instancia] = ip_elastica

# Crear las instancias y asociar IPs elásticas
for nombre_instancia, nombre_sg in zip(nombres_instancias, nombres_sg):
    instances = aws.create_instance(ami, 1, instance_type, key_name, nombre_instancia, nombre_sg)
    if instances is not None and len(instances) > 0:
        id_instancia = instances[0].id

        # Esperar explícitamente 30 segundos para asegurarse de que la instancia está en estado "running"
        time.sleep(30)

        # Verificar si la instancia está en estado "running"
        instance_description = aws.describe_instance(id_instancia)
        if instance_description and 'Reservations' in instance_description:
            instance_state = instance_description['Reservations'][0]['Instances'][0]['State']['Name']
            if instance_state == 'running':
                # Intentar asignar la IP elástica varias veces si no funciona a la primera
                for _ in range(3):
                    try:
                        aws.associate_elastic_ip(ips_elasticas[nombre_instancia], id_instancia)
                        print(f'IP elástica asignada a la instancia {nombre_instancia}')
                        break
                    except Exception as e:
                        print(f'Error al asignar la IP elástica a la instancia {nombre_instancia}: {e}')
                        time.sleep(10)
            else:
                print(f'La instancia {id_instancia} no está en estado "running". Estado actual: {instance_state}')
        else:
            print(f'Error al obtener la descripción de la instancia {id_instancia}')
    else:
        print(f'No se pudieron crear instancias para {nombre_instancia}')