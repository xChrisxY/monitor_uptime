from datetime import datetime, timezone 
import time
import ssl
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from config import *

def now_iso():
    """Retorna la fecha/hora actual en formato ISO 8601 UTC."""
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def check_url(url, timeout):
    start = time.time()

    try:
        # Crear request con User-Agent
        req = Request(
            url,
            headers={'User-Agent': 'UptimeMonitor/1.0'}
        )

        # Nota: urlopen sigue redirecciones por defecto
        context = ssl.create_default_context()
        with urlopen(req, timeout=timeout, context=context) as resp:
            status_code = resp.status
            latency_ms = int((time.time() - start) * 1000)

            # 2xx y 3xx = éxito
            success = 200 <= status_code < 400

            return {
                'success': success,
                'status_code': status_code,
                'error': None if success else f"HTTP {status_code}",
                'latency_ms': latency_ms
            }

    except HTTPError as e:
        latency_ms = int((time.time() - start) * 1000)
        return {
            'success': False,
            'status_code': e.code,
            'error': f"HTTP {e.code}",
            'latency_ms': latency_ms
        }

    except URLError as e:
        latency_ms = int((time.time() - start) * 1000)
        reason = str(e.reason) if e.reason else 'Connection error'
        return {
            'success': False,
            'status_code': None,
            'error': reason,
            'latency_ms': latency_ms
        }

    except TimeoutError:
        latency_ms = int((time.time() - start) * 1000)
        return {
            'success': False,
            'status_code': None,
            'error': f'Timeout after {timeout}s',
            'latency_ms': latency_ms
        }

    except Exception as e:
        latency_ms = int((time.time() - start) * 1000)
        return {
            'success': False,
            'status_code': None,
            'error': str(e),
            'latency_ms': latency_ms
        }


def send_alert(monitor, is_down, result):

    status = "DOWN" if is_down else "UP"
    suffix = "" if is_down else " (recuperado)"

    # Truncar nombre si es muy largo (límite de SNS: 100 chars en subject)
    name = monitor['name'][:50]

    subject = f"[{status}] {name}{suffix}"

    # Construir el mensaje
    if result.get('status_code'):
        resultado = f"HTTP {result['status_code']}"
    else:
        resultado = result.get('error', 'Unknown error')

    message = f"""Monitor:   {monitor['name']}
      URL:       {monitor['url']}
      Estado:    {status}
      Resultado: {resultado}
      Latencia:  {result['latency_ms']} ms
      Fallos:    {monitor.get('consecutive_failures', 0)} consecutivos
      Hora:      {now_iso()}
      """

    try:
        sns.publish(
            TopicArn=TOPIC_ARN,
            Subject=subject,
            Message=message
        )
        print(f"Alert sent: {subject}")
        return True
    except Exception as e:
        print(f"Failed to send alert: {e}")
        return False

def get_all_monitors():
    """Obtiene todos los monitores de DynamoDB."""
    monitors = []
    scan_kwargs = {}

    while True:
        resp = table.scan(**scan_kwargs)
        monitors.extend(resp.get('Items', []))

        if 'LastEvaluatedKey' in resp:
            scan_kwargs['ExclusiveStartKey'] = resp['LastEvaluatedKey']
        else:
            break

    return monitors


def process_monitor(monitor):
    """
    Revisa un monitor y calcula el nuevo estado.

    Returns:
        dict con:
        - monitor_id
        - new_status
        - result (del check)
        - should_alert
        - is_down
    """
    monitor_id = monitor['id']
    current_status = monitor.get('last_status', 'UNKNOWN')
    consecutive_failures = int(monitor.get('consecutive_failures', 0))

    # Revisar la URL
    result = check_url(monitor['url'], REQUEST_TIMEOUT)

    # Calcular nuevo estado
    if result['success']:
        # Éxito
        new_status = 'UP'
        new_failures = 0

        # ¿Alertar por recuperación?
        should_alert = (current_status == 'DOWN')
        is_down = False

    else:
        # Fallo
        new_failures = consecutive_failures + 1

        if new_failures >= FAILURE_THRESHOLD:
            new_status = 'DOWN'
            # ¿Alertar por caída?
            should_alert = (current_status != 'DOWN')
            is_down = True
        else:
            # Aún no alcanza el umbral
            new_status = current_status  # Mantener estado actual
            should_alert = False
            is_down = False

    return {
        'monitor_id': monitor_id,
        'monitor': monitor,
        'new_status': new_status,
        'new_failures': new_failures,
        'result': result,
        'should_alert': should_alert,
        'is_down': is_down
    }


def update_monitor_status(monitor_id, new_status, new_failures, result):
    """Actualiza el estado del monitor en DynamoDB."""

    update_expression = """
        SET last_status = :status,
            last_checked = :checked,
            last_latency_ms = :latency,
            consecutive_failures = :failures
    """

    expression_values = {
        ':status': new_status,
        ':checked': now_iso(),
        ':latency': result['latency_ms'],
        ':failures': new_failures
    }

    # Agregar status_code o error según corresponda
    if result.get('status_code'):
        update_expression += ", last_status_code = :code"
        expression_values[':code'] = result['status_code']
        # Remover last_error si existía
        update_expression += " REMOVE last_error"
    elif result.get('error'):
        update_expression += ", last_error = :error"
        expression_values[':error'] = result['error']
        # Remover last_status_code si existía
        update_expression += " REMOVE last_status_code"

    try:
        table.update_item(
            Key={'id': monitor_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ConditionExpression='attribute_exists(id)'
        )
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            # El monitor fue borrado mientras lo revisábamos
            print(f"Monitor {monitor_id} was deleted, skipping update")
            return False
        raise







