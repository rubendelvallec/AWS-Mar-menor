from flask import Flask, request, jsonify
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Attr

app = Flask(__name__)

tabla_dy = 'proy-tabla'
region = 'us-east-1'

dynamodb = boto3.resource('dynamodb', region_name=region)
table = dynamodb.Table(tabla_dy)


def media(items, field: str):
    """
    Calcula la media de una lista numérica almacenada en el atributo `field`
    (lista de Decimal / float / int).
    """
    # Convertimos cada valor a float por si vienen como Decimal
    valores = []
    for i in items:
        valores.append(float(i[field]))

    media_global = sum(valores) / len(valores)
    return media_global

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200


@app.route('/temp', methods=['GET'])
def get_temp():
    y, m = request.args.get('year'), request.args.get('month')
    mes_anyo = f"{m}-{y}"
    response = table.scan(
        FilterExpression=Attr("mes_anyo").eq(mes_anyo)
    )

    items = response.get('Items',[])
    if not items:
        return jsonify({"error": f"Datos no encontrados para {mes_anyo}"}, 404)

    media_temp = media(items, "media")

    return jsonify({
    f"Media de temperatura del mes {mes_anyo}": media_temp
    })

@app.route('/maxdiff', methods=['GET'])
def get_maxdiff():
    y, m = int(request.args.get('year')), int(request.args.get('month'))
    mes_anyo = f"{m}-{y}"
    response = table.scan(
        FilterExpression=Attr("mes_anyo").eq(mes_anyo)
    )
    items = response.get('Items',[])
    if not items:
        return jsonify({"error": f"Datos no encontrados para {mes_anyo}"}, 404)

    max_act = 0
    for i in items:
        if float(i['media']) > max_act:
             max_act = float(i['media'])

    if m == 1:
        m_2 = 12
        y_2 = y-1

    else:
        m_2 = m-1
        y_2 = y

    mes_anyo_ant = f"{m_2}-{y_2}"
    response_ant = table.scan(
        FilterExpression=Attr("mes_anyo").eq(mes_anyo_ant)
    )
    items_ant = response_ant.get('Items',[])
    if not items_ant:
        return jsonify({"error": f"Datos no encontrados para mes anterior"}, 404)

    max_ant = 0
    for i in items_ant:
        if float(i['media']) > max_ant:
             max_ant = float(i['media'])

    max_diff = max_act-max_ant
    return jsonify({ 
        f"Diferencia maxima de temperatura del mes {mes_anyo}": max_diff
    })

@app.route('/sd', methods=['GET'])
def get_sd():
    y, m = request.args.get('year'), request.args.get('month')
    mes_anyo = f"{m}-{y}"
    response = table.scan(
        FilterExpression=Attr("mes_anyo").eq(mes_anyo)
    )
    items = response.get('Items',[])
    if not items:
        return jsonify({"error": f"Datos no encontrados para {mes_anyo}"}, 404)

    max = 0
    for i in items:
        if float(i['desviacion']) > max:
             max = float(i['desviacion'])

    return jsonify({
    f"Maxima desviacion del mes {mes_anyo}": max
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

