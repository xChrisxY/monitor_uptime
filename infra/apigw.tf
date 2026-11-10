# HTTP API
resource "aws_apigatewayv2_api" "api" {
  name = "${var.project_name}-api"
  description = "API para gestionar monitores de uptime"
  protocol_type = "HTTP"

  # CORS: permite peticiones desde cualquier origen
  cors_configuration {
      allow_origins = [ "*" ]
      allow_methods = [ "GET", "POST", "DELETE", "PATCH", "OPTIONS" ]
      allow_headers = [ "Content-Type", "Authorization" ]
      max_age = 300
  }

  tags = {
      Name = "${var.project_name}-api"
  }
}

# INTEGRATION (conexión con Lambda)
resource "aws_apigatewayv2_integration" "lambda" {
  api_id = aws_apigatewayv2_api.api.id
  integration_type = "AWS_PROXY"

  # URI de la Lambda
  integration_uri = aws_lambda_function.api.invoke_arn
  integration_method = "POST"
  payload_format_version = "2.0"
}

# ROUTES (endpoints)
resource "aws_apigatewayv2_route" "create_monitor" {
  api_id = aws_apigatewayv2_api.api.id
  route_key = "POST /monitors"
  target = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_route" "list_monitor" {
  api_id = aws_apigatewayv2_api.api.id
  route_key = "GET /monitors"
  target = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_route" "get_monitor" {
  api_id = aws_apigatewayv2_api.api.id
  route_key = "GET /monitors/{id}"
  target = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_route" "delete_monitor" {
  api_id = aws_apigatewayv2_api.api.id
  route_key = "DELETE /monitors/{id}"
  target = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_route" "update_monitor" {
  api_id = aws_apigatewayv2_api.api.id
  route_key = "PATCH /monitors/{id}"
  target = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# STAGE (ambiente de despliegue)
resource "aws_apigatewayv2_stage" "default" {
  api_id = aws_apigatewayv2_api.api.id
  name = "$default"
  auto_deploy = true

  tags = {
    Name = "${var.project_name}-api-stage"
  }
}

# PERMISO PARA INVOCAR LAMBDA
resource "aws_lambda_permission" "api_gateway" {
  statement_id = "AllowAPIGateway"
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal = "apigateway.amazonaws.com"
  source_arn = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}