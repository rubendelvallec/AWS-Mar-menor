import json, urllib.parse
import boto3
import csv
import io
import os

# Clientes de AWS
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
datosTable = dynamodb.Table('proy-tabla')

def lambda_handler(event, context):
    
    # 1. Obtener detalles del archivo subido desde el evento S3
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    
    print(f"Procesando archivo: {file_key} del bucket: {bucket_name}")
    
    # 2. Leer el archivo CSV desde S3
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    content = response['Body'].read().decode('utf-8')
    
    # 3. Parsear el CSV
    csv_reader = csv.DictReader(io.StringIO(content), delimiter=',') # Ajusta delimitador si es necesario
    
    items_processed = 0
    
    for row in csv_reader:
        # Formato esperado del CSV: Fecha, Medias, Desviaciones
        fecha = row['Fecha'] # Ej: 22/03/2017
        media = row['Medias']
        desviacion = row['Desviaciones']
        
       
        partes_fecha = fecha.split('/')
        if len(partes_fecha) == 3:
            dia_normalizado = int(partes_fecha[2])
            mes_normalizado = int(partes_fecha[1])
            anio = partes_fecha[0]
            mes_anyo = f"{mes_normalizado}-{anio}" # Ej: "03-2017" se convierte en "3-2017"
            fecha = f"{anio}/{mes_normalizado}/{dia_normalizado}" # Ej: "2017/03/22" se convierte en "2017/3/22"
        else:
            print(f"Formato de fecha incorrecto: {fecha}")
            continue

        # 4. Insertar en DynamoDB
        try:
            datosTable.put_item(
                Item={
                    'fecha': fecha,         # Partition Key
                    'mes_anyo': mes_anyo,
                    'media': media,
                    'desviacion': desviacion
                }
            )
            items_processed += 1
        except Exception as e:
            print(f"Error insertando {fecha}: {str(e)}")

    return {
        'statusCode': 200,
        'body': json.dumps(f'Procesados {items_processed} registros.')
    }