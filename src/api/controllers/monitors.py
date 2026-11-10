"""
Lambda que maneja el CRUD de monitores.
Recibe eventos de API Gateway (HTTP API, payload v2.0)
"""
import json
from utils import *
from config import *
from botocore.exceptions import ClientError

def create_monitor(body):
      
      try:
            data = json.loads(body) if body else {}
      except json.JSONDecodeError: 
            return error_response(400, 'Invalid JSON body')

      name = data.get('name', '').strip() if data.get('name') else ''
      url = data.get('url', '').strip() if data.get('url') else ''

      valid, error = validate_name(name)
      if not valid:
            return error_response(400, error)

      # Verificar lista de monitores
      count_response = table.scan(Select='COUNT')
      current_count = count_response.get('Count', 0)

      if current_count >= MAX_MONITORS:
            return error_response(409, f"Maximum of {MAX_MONITORS} monitors reached")
      
      # Crear el monitor
      monitor_id = generate_id()
      now = now_iso()

      monitor = {
            'id' : monitor_id, 
            'name': name, 
            'url': url, 
            'created_at': now, 
            'last_status': 'UNKNOWN', 
            'consecutive_failures': 0
      }

      try: 
            table.put_item(
                  Item=monitor, 
                  ConditionExpression='attribute_not_exists(id)'
            )
      except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                  # ID ya existe (muy improbable), reintentar
                  return create_monitor(body)
            raise

      return response(201, monitor)

      
def list_monitors():
      monitors = []
      scan_kwargs = {}

      # Paginar el scan
      while True:
            resp = table.scan(**scan_kwargs)
            monitors.extend(resp.get('Items', []))

            # ¿Hay más páginas?
            if 'LastEvaluatedKey' in resp:
                  scan_kwargs['ExclusiveStartKey'] = resp['LastEvaluatedKey']
            else:
                  break

      # Convertir números de Decimal a int/float para JSON
      for m in monitors:
            if 'consecutive_failures' in m:
                  m['consecutive_failures'] = int(m['consecutive_failures'])
            if 'last_status_code' in m:
                  m['last_status_code'] = int(m['last_status_code'])
            if 'last_latency_ms' in m:
                  m['last_latency_ms'] = int(m['last_latency_ms'])

      return response(200, {
            'count': len(monitors),
            'monitors': monitors
      })

def get_monitors(monitor_id):

    resp = table.get_item(Key={'id': monitor_id})
    monitor = resp.get('Item')

    if not monitor:
        return error_response(404, "Monitor not found")

    # Convertir Decimal a int
    if 'consecutive_failures' in monitor:
        monitor['consecutive_failures'] = int(monitor['consecutive_failures'])
    if 'last_status_code' in monitor:
        monitor['last_status_code'] = int(monitor['last_status_code'])
    if 'last_latency_ms' in monitor:
        monitor['last_latency_ms'] = int(monitor['last_latency_ms'])

    return response(200, monitor)


def get_monitor(monitor_id):
    """GET /monitors/{id} - Obtener un monitor específico."""

    resp = table.get_item(Key={'id': monitor_id})
    monitor = resp.get('Item')

    if not monitor:
        return error_response(404, "Monitor not found")

    # Convertir Decimal a int
    if 'consecutive_failures' in monitor:
        monitor['consecutive_failures'] = int(monitor['consecutive_failures'])
    if 'last_status_code' in monitor:
        monitor['last_status_code'] = int(monitor['last_status_code'])
    if 'last_latency_ms' in monitor:
        monitor['last_latency_ms'] = int(monitor['last_latency_ms'])

    return response(200, monitor)


def delete_monitor(monitor_id):

    try:
        table.delete_item(
            Key={'id': monitor_id},
            ConditionExpression='attribute_exists(id)'
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return error_response(404, "Monitor not found")
        raise

    return response(204, None)


def update_monitor(monitor_id, body):

    # Parsear el body
    try:
        data = json.loads(body) if body else {}
    except json.JSONDecodeError:
        return error_response(400, "Invalid JSON body")

    # Verificar que el monitor existe
    resp = table.get_item(Key={'id': monitor_id})
    if not resp.get('Item'):
        return error_response(404, "Monitor not found")

    # Construir la actualización
    update_parts = []
    expression_values = {}
    expression_names = {}

    # Actualizar name si se proporciona
    if 'name' in data:
        name = data['name'].strip() if data['name'] else ''
        valid, error = validate_name(name)
        if not valid:
            return error_response(400, error)

        update_parts.append('#n = :name')
        expression_values[':name'] = name
        expression_names['#n'] = 'name'

    # Actualizar url si se proporciona
    if 'url' in data:
        url = data['url'].strip() if data['url'] else ''
        valid, error = validate_url(url)
        if not valid:
            return error_response(400, error)

        update_parts.append('#u = :url')
        expression_values[':url'] = url
        expression_names['#u'] = 'url'

        # Si cambia la URL, reiniciar el estado
        update_parts.append('last_status = :status')
        update_parts.append('consecutive_failures = :failures')
        expression_values[':status'] = 'UNKNOWN'
        expression_values[':failures'] = 0

    if not update_parts:
        return error_response(400, "No valid fields to update")

    # Ejecutar la actualización
    update_expression = 'SET ' + ', '.join(update_parts)

    updated = table.update_item(
        Key={'id': monitor_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values,
        ExpressionAttributeNames=expression_names if expression_names else None,
        ReturnValues='ALL_NEW'
    )

    monitor = updated['Attributes']

    # Convertir Decimal a int
    if 'consecutive_failures' in monitor:
        monitor['consecutive_failures'] = int(monitor['consecutive_failures'])

    return response(200, monitor)