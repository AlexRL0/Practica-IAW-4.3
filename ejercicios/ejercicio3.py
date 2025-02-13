from common import aws_resource_functions as aws

# ID del AMI
ami = 'ami-04b4f1a9cf54c11d0'

# Tipo de instancia
instance_type = 't2.micro'

# Clave privada
key_name = 'vockey'

# Nombres de las instancias y grupos de seguridad
nombres_instancias = ['frontend-1', 'frontend-2', 'backend', 'balanceador', 'nfs']
nombres_sg = ['frontend-sg', 'backend-sg', 'balanceador-sg', 'nfs-sg']

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
    print(f'IP elástica asignada {ip_elastica} para {nombre_instancia}')

# Crear las instancias y asociar IPs elásticas
for nombre_instancia, nombre_sg in zip(nombres_instancias, nombres_sg):
    id_instancia = aws.create_instance(ami, 1, instance_type, key_name, nombre_instancia, nombre_sg)
    print(f'La instancia {id_instancia[0].id} ha sido creada. Esperando a que esté en estado "running"...')
    aws.associate_elastic_ip(ips_elasticas[nombre_instancia], id_instancia[0].id)
    print(f'IP elástica {ips_elasticas[nombre_instancia]} asociada a la instancia {id_instancia[0].id}.')

# Listar las instancias
aws.list_instances()