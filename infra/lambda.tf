# EMPAQUETADO DEL CÓDIGO (ZIP)

data "archive_file" "api_lambda" {
  type = "zip"
  source_file = "${path.module}/../src/api/handler.py"
  output_path = "${path.module}/build/api.zip"
}

data "archive_file" "checker_lambda" {
  type = "zip" 
  source_file = "${path.module}/../src/checker/handler.py"
  output_path = "${path.module}/build/checker.zip"
}

resource "aws_cloudwatch_log_group" "api_lambda" {
  name              = "/aws/lambda/${var.project_name}-api-fn"
  retention_in_days = 7  # Los logs se borran después de 7 días

  tags = {
    Name = "${var.project_name}-api-logs"
  }
}

resource "aws_cloudwatch_log_group" "checker_lambda" {
  name              = "/aws/lambda/${var.project_name}-checker-fn"
  retention_in_days = 7

  tags = {
    Name = "${var.project_name}-checker-logs"
  }
}

### LAMBDA API
resource "aws_lambda_function" "api" {
  function_name = "${var.project_name}-api-fn"
  description = "Maneja el CRUD de monitores"

  # Código
  filename = data.archive_file.api_lambda.output_path
  source_code_hash = data.archive_file.api_lambda.output_base64sha256
  handler = "handler.lambda_handler"
  runtime = "python3.12"

  # Recursos
  memory_size = 128
  timeout = 10

  role = aws_iam_role.api_lambda.arn

  # Variables de entorno
  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.monitors.name
      MAX_MONITORS = tostring(var.max_monitors)
    }
  }

  # Depende del log group
  depends_on = [ 
    aws_cloudwatch_log_group.api_lambda, 
    aws_iam_role_policy_attachment.api_lambda_logs
  ]

  tags = {
    Name = "${var.project_name}-api-fn"
  }
  
}


# LAMBDA CHECKER
resource "aws_lambda_function" "checker" {
  function_name = "${var.project_name}-checker-fn"
  description = "Revisa el estado de los sitios monitoreados"

  # Código
  filename = data.archive_file.checker_lambda
  source_code_hash = data.archive_file.checker_lambda.output_base64sha256
  handler = "handler.lambda_handler"
  runtime = "python3.12"

  # Recursos
  memory_size = 128
  timeout = 60

  # Rol con permisos
  role = aws_iam_role.api_lambda.arn

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.monitors.name 
      TOPIC_ARN = aws_sns_topic.alerts.arn
      REQUEST_TIMEOUT_SECONDS = tostring(var.request_timeout_seconds)
      FAILURE_THRESHOLD = tostring(var.failure_threshold)
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.checker_lambda,
    aws_iam_role_policy_attachment.checker_lambda_logs
  ]

  tags = {
    Name = "${var.project_name}-checker-fn"
  }
}