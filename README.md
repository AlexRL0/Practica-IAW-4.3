# Practica-IAW-4.3- Ejercicios con AWS-python-boto3

## Ejercicio 1. Crear un grupo de seguridad con el nombre backend-sg con las reglas Acceso SSH (puerto 22/TCP) desde cualquier dirección IP y Acceso al puerto 3306/TCP desde cualquier dirección IP al grupo de seguridad:

```bash
from common import aws_resource_functions as aws

# Hacer las reglas de entrada del grupo de seguridad
ingress_permissions = [
    {'CidrIp': '0.0.0.0/0', 'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22},
    {'CidrIp': '0.0.0.0/0', 'IpProtocol': 'tcp', 'FromPort': 3306, 'ToPort': 3306}
]

# Definir el nombre y la descripción del grupo de seguridad
sg_name = 'backend-sg'
sg_description = 'Grupo de seguridad para el backend'

# Crear el grupo de seguridad
aws.create_security_group(sg_name, sg_description, ingress_permissions)

# Listar los grupos de seguridad
aws.list_security_groups()
```

![Ejercicio1](imagenes/ejercicio1-4.3.png)
![Ejercicio1-parte-2](imagenes/ejercicio1-4.3-parte-2.png)

## Ejercicio 2. Escriba un script de Python para crear una instancia EC2 que tengas las siguientes características: Identificador de la AMI: ami-08e637cea2f053dfa, esta AMI se corresponde con la imagen Red Hat Enterprise Linux 9 (HVM), número de instancias: 1, tipo de instancia: t2.micro, clave privada: vockey, grupo de seguridad: backend-sg, nombre de la instancia: backend.

```bash
from common import aws_resource_functions as aws

# ID del AMI
ami = 'ami-08e637cea2f053dfa'

# Tipo de instancia
instance_type = 't2.micro'

# Clave privada
key_name = 'vockey'

# Nombre de la instancia y grupo de seguridad
instance_name = 'backend'
sg_name = 'backend-sg'

# Comprobar que el grupo de seguridad existe
if aws.security_group_exists(sg_name) == False:
    print('The security group does not exist')
    exit()

# Crear la instancia
aws.create_instance(ami, 1, instance_type, key_name, instance_name, sg_name)

# Listar las instancias
aws.list_instances()
```

![Ejercicio2](imagenes/ejercicio2-4.3.png)
![Ejercicio2-parte-2](imagenes/ejercicio2-4.3-parte-2.png)

## Ejercicio 3.1. Crear un script para crear la infraestructura de la práctica 1.11.

```bash
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

# Crear las instancias y asociar IPs elásticas
for nombre_instancia, nombre_sg in zip(nombres_instancias, nombres_sg):
    try:
        instances = aws.create_instance(ami, 1, instance_type, key_name, nombre_instancia, nombre_sg)
        if instances and len(instances) > 0:
            id_instancia = instances[0].id
            print(f'La instancia {id_instancia} ha sido creada. Esperando a que esté en estado "running"...')
            time.sleep(60)  # Espera de 60 segundos para asegurar que la instancia esté en estado running
            aws.associate_elastic_ip(ips_elasticas[nombre_instancia], id_instancia)
            print(f'IP elástica {ips_elasticas[nombre_instancia]} asociada a la instancia {id_instancia}.')
        else:
            print(f'Error al crear la instancia {nombre_instancia}')
    except Exception as e:
        print(f'Ocurrió un error al crear y asociar IP para la instancia {nombre_instancia}: {e}')

# Listar las instancias
aws.list_instances()
```

![Ejercicio3](imagenes/ejercicio3-4.1.png)
![Ejercicio3-parte-2](imagenes/ejercicio3-parte2-4.1.png)
![Ejercicio3-parte-3](imagenes/ejercicio3-parte3-4.1.png)
![Ejercicio3-parte-4](imagenes/ejercicio3-parte4-4.1.png)
![Ejercicio3-parte-5](imagenes/ejercicio3-parte5-4.1.png)
![Ejercicio3-parte-6](imagenes/ejercicio3-parte6-4.1.png)

## Ejercicio 3.2. Crear un script para la eliminación de la infraestructura de la práctica 1.11.

```bash
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
```

![Ejercicio3-2.parte-7](imagenes/ejercicio3-parte7-4.1.png)
![Ejercicio3-2-parte-8](imagenes/ejercicio3-parte8-4.1.png)
![Ejercicio3-2-parte-9](imagenes/ejercicio3-parte9-4.1.png)
