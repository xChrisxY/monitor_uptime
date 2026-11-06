import json 
from datetime import datetime, timezone
import uuid
import ipaddress
from urllib.parse import urlparse

def response(status_code, body):
    """Construye la respuesta en el formato que espera API Gateway."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(body)
    }


def error_response(status_code, message):
    """Construye una respuesta de error."""
    return response(status_code, {'error': message})


def generate_id():
    """Genera un ID único de 8 caracteres hexadecimales."""
    return uuid.uuid4().hex[:8]


def now_iso():
    """Retorna la fecha/hora actual en formato ISO 8601 UTC."""
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def is_private_ip(hostname):
    """
    Verifica si un hostname es una IP privada, loopback o link-local.
    Retorna True si es una IP que no debemos visitar.
    """
    try:
        ip = ipaddress.ip_address(hostname)
        return ip.is_private or ip.is_loopback or ip.is_link_local
    except ValueError:
        # No es una IP literal, es un dominio (OK)
        return False


def validate_url(url):
    """
    Valida la URL del monitor.
    Retorna (True, None) si es válida, o (False, mensaje_error) si no.
    """
    if not url:
        return False, "url is required"

    if len(url) > 2048:
        return False, "url must be 2048 characters or less"

    if not url.startswith('https://'):
        return False, "url must start with https://"

    try:
        parsed = urlparse(url)
        hostname = parsed.hostname

        if not hostname:
            return False, "url must have a valid hostname"

        # Rechazar IPs privadas/loopback/link-local
        if is_private_ip(hostname):
            return False, "url cannot point to private, loopback, or link-local addresses"

    except Exception:
        return False, "url is not valid"

    return True, None


def validate_name(name):
    """
    Valida el nombre del monitor.
    Retorna (True, None) si es válido, o (False, mensaje_error) si no.
    """
    if not name:
        return False, "name is required"

    if not isinstance(name, str):
        return False, "name must be a string"

    name = name.strip()

    if len(name) < 1:
        return False, "name cannot be empty"

    if len(name) > 60:
        return False, "name must be 60 characters or less"

    return True, None