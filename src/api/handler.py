# LAMBDA PRINCIPAL
import json
from controllers.monitors import *

def lambda_handler(event, context):
      # Enruta según la routeKey del evento de API Gateway

      print(f"Event: {json.dumps(event)}")

      route_key = event.get('routeKey', '')
      path_params = event.get('pathParameters') or {}
      body = event.get('body', '')

      routes = {
            'POST /monitors': lambda: create_monitor(body),
            'GET /monitors': lambda: list_monitors(),
            'GET /monitors/{id}': lambda: get_monitor(path_params.get('id')), 
            'DELETE /monitors/{id}': lambda: delete_monitor(path_params.get('id')), 
            'PATCH /monitors/{id}': lambda: update_monitor(path_params.get('id'), body), 
      }

      handler = routes.get(route_key)

      if handler: 
            try:
                  return handler()
            except Exception as e:
                  print(f"Error: {str(e)}")
                  return error_response(500, "Internal Server Error")
      else:
            return error_response(404, f"Route not found: {route_key}")