Proyecto AWS: Ingesta de datos y despliegue de aplicación Flask
Proyecto de procesamiento de datos de temperatura en AWS. La solución
combina servicios serverless para ingerir y analizar datos, una API web
desarrollada con Flask y una arquitectura de contenedores desplegada con
Amazon ECS y un Application Load Balancer.
Arquitectura y componentes
1. Ingesta y procesamiento serverless
Servicios utilizados: Amazon S3, AWS Lambda, Amazon DynamoDB y Amazon
SNS.
- S3 (proy-ingestadatos): almacena el archivo CSV original y
  dispara el procesamiento al recibir nuevos archivos.
- Lambda (proy-funcion-procesador-datos): lee el CSV, procesa
  sus registros, obtiene el campo mes_anyo a partir de la fecha y
  guarda los datos en DynamoDB.
- DynamoDB (proy-tabla): almacena los campos fecha,
  mes_anyo, media y desviacion. La clave de partición indicada
  en la guía es fecha.
- Lambda (proy-funcion-notificacion): procesa las inserciones
  nuevas de DynamoDB y comprueba el valor de desviacion.
- SNS (proy-alarma-temperatura): envía una notificación por
  correo cuando la desviación supera 0.5.
La guía indica usar Python 3.9 para las funciones Lambda, el rol
LabRole y un tiempo de espera de un minuto para la función
procesadora. La notificación se configura mediante un flujo de DynamoDB
con tamaño de lote de 500.
Comprobación esperada según la guía: aproximadamente 380 elementos
en DynamoDB y 36 correos de alerta. Son cifras orientativas que dependen
de los datos procesados.
2. Aplicación web con Flask y Docker
La API consulta los datos de DynamoDB usando boto3. La aplicación se
ejecuta en el puerto 5000 y se empaqueta en una imagen Docker.
Archivos de la aplicación:
- funcion.py: aplicación Flask, conexión con DynamoDB y rutas de
  consulta.
- requirements.txt: dependencias de Python, entre ellas Flask y
  boto3.
- Dockerfile: imagen base python:3.8-alpine, directorio de trabajo
  /app, instalación de dependencias y arranque de la aplicación.
Rutas documentadas:
  Ruta         Propósito
  /temp      Consulta de temperaturas/datos procesados.
  /maxdiff   Consulta relacionada con la diferencia máxima.
  /sd        Consulta relacionada con la desviación estándar.
  /health    Comprobación de estado para el balanceador.
La implementación concreta de las respuestas de cada ruta debe
consultarse en el código de la aplicación.
3. Registro y orquestación de contenedores
- Amazon ECR (proy-repo): almacena la imagen Docker de la
  aplicación.
- Amazon ECS (proy-cluster): administra el despliegue de
  contenedores.
- Definición de tarea (proy-task): usa el contenedor
  proy-container, con el puerto TCP 5000.
- Servicio ECS (proy-ecs-service): mantiene dos tareas deseadas
  en configuración de tipo réplica.
- Application Load Balancer (proy-alb): expone la aplicación
  mediante HTTP en el puerto 80.
- Grupo de destino (proy-tg-flask): dirige el tráfico al puerto
  5000 y realiza comprobaciones de salud en /health.
- VPC Endpoint de DynamoDB: permite el acceso a DynamoDB desde la
  VPC a través del endpoint de tipo Gateway indicado en la guía.
La infraestructura de red se despliega mediante CloudFormation con la
pila proy-pila y la plantilla proy-plantilla.
