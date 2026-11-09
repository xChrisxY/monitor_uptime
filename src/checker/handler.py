import json
from config import *
from utils import *
from concurrent.futures import ThreadPoolExecutor, as_completed

def lambda_handler(event, context):
    """
    Punto de entrada de la Lambda.
    Se ejecuta cada 5 minutos vía EventBridge Scheduler.
    """

    print(f"Event: {json.dumps(event)}")
    print(f"Timeout: {REQUEST_TIMEOUT}s, Threshold: {FAILURE_THRESHOLD}")

    # Obtener todos los monitores
    monitors = get_all_monitors()
    print(f"Found {len(monitors)} monitors")

    if not monitors:
        return {
            'checked': 0,
            'up': 0,
            'down': 0,
            'alerts_sent': 0
        }

    # Revisar todos en paralelo
    results = []
    max_workers = min(10, len(monitors))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Enviar todas las tareas
        future_to_monitor = {
            executor.submit(process_monitor, m): m
            for m in monitors
        }

        # Recoger resultados
        for future in as_completed(future_to_monitor):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                monitor = future_to_monitor[future]
                print(f"Error checking {monitor['id']}: {e}")

    # Procesar resultados
    stats = {'checked': 0, 'up': 0, 'down': 0, 'alerts_sent': 0}

    for r in results:
        stats['checked'] += 1

        # Actualizar en DynamoDB
        updated = update_monitor_status(
            r['monitor_id'],
            r['new_status'],
            r['new_failures'],
            r['result']
        )

        if not updated:
            continue

        # Contar estados
        if r['new_status'] == 'UP':
            stats['up'] += 1
        elif r['new_status'] == 'DOWN':
            stats['down'] += 1

        # Enviar alerta si es necesario
        if r['should_alert']:
            # Actualizar el monitor con los nuevos valores para la alerta
            alert_monitor = r['monitor'].copy()
            alert_monitor['consecutive_failures'] = r['new_failures']

            if send_alert(alert_monitor, r['is_down'], r['result']):
                stats['alerts_sent'] += 1

    print(f"Results: {stats}")
    return stats