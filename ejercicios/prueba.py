from common import aws_resource_functions as aws
import time

# Ejemplo de prueba para asociar una IP elástica manualmente
public_ip = '54.156.105.125'  # Reemplaza con una de las IPs asignadas
instance_id = 'i-0db659bd94693b787'  # Reemplaza con uno de los IDs de instancia creados

aws.associate_elastic_ip(public_ip, instance_id)
