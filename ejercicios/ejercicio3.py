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

# Comprobar que los grupos de seguridad existen
for nombre_sg in nombres_sg:
    if not aws.security_group_exists(nombre_sg):
        print(f'El grupo de seguridad {nombre_sg} no existe')
        exit()

# Crear IPs elásticas
ips_elasticas = {}
for nombre_instancia in nombres_instancias:
    ip_elastica = aws.allocate_elastic_ip()
    ips_elasticas[nombre_instancia] = ip_elastica
    print(f'IP elástica asignada {ip_elastica} para {nombre_instancia}')

# Crear las instancias y asociar IPs elásticas
for nombre_instancia, nombre_sg in zip(nombres_instancias, nombres_sg):
    id_instancia = aws.create_instance(ami, 1, instance_type, key_name, nombre_instancia, nombre_sg)
    aws.wait_instance_running(id_instancia)
    ip_elastica = ips_elasticas[nombre_instancia]
    aws.associate_elastic_ip(id_instancia, ip_elastica)

# Listar las instancias
aws.list_instances()