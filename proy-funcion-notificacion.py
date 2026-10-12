# Stock Check Lambda function
#
# This function is triggered when values are inserted into the Inventory DynamoDB table.
# Inventory counts are checked and if an item is out of stock, a notification is sent to an SNS Topic.
import json, boto3

# This handler is run every time the Lambda function is triggered
def lambda_handler(event, context):
    # Show the incoming event in the debug log
    print("Event received by Lambda function: " + json.dumps(event, indent=2))
    alertas_enviadas = 0
    # For each inventory item added, check if the count is zero
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            try:
                newImage = record['dynamodb']['NewImage']
            
                desviacion_str = newImage['desviacion']['S']
                fecha = newImage['fecha']['S']
                desviacion_val = float(desviacion_str)

                if desviacion_val > 0.5:
                    mensaje = (
                        f"ALERTA AQUASENSE:\n"
                        f"Fecha: {fecha}\n"
                        f"Desviación detectada: {desviacion_val}\n"
                        f"Umbral permitido: 0.5"
                    )
                    sns = boto3.client('sns')

                    alertTopic = 'proy-alarma-temperatura'
                    
                    snsTopicArn = [t['TopicArn'] for t in sns.list_topics()['Topics']
                            if t['TopicArn'].lower().endswith(':' + alertTopic.lower())]
                    for i in range(0, len(snsTopicArn)):
                        
                        sns.publish(
                            TopicArn=snsTopicArn[i],
                            Message=mensaje,
                            Subject='¡Alerta Crítica Mar Menor!'
                        )
                        print(f"Alerta enviada para fecha {fecha}")
                        alertas_enviadas += 1
                    
            except KeyError as e:
                print(f"Falta algún campo en el registro: {e}")
            except ValueError as e:
                print(f"Error convirtiendo desviación a número: {e}")

    # Finished!
    return 'Successfully processed {} records.'.format(len(event['Records']))
