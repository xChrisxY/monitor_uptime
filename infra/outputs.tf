
# ============================================
# OUTPUTS DE LA API
# ============================================

output "api_url" {
  description = "URL base de la API (para usar con curl)"
  value       = aws_apigatewayv2_api.api.api_endpoint
}

output "api_id" {
  description = "ID de la API Gateway"
  value       = aws_apigatewayv2_api.api.id
}

# ============================================
# OUTPUTS DE DYNAMODB
# ============================================

output "table_name" {
  description = "Nombre de la tabla de DynamoDB"
  value       = aws_dynamodb_table.monitors.name
}

output "table_arn" {
  description = "ARN de la tabla de DynamoDB"
  value       = aws_dynamodb_table.monitors.arn
}

# ============================================
# OUTPUTS DE SNS
# ============================================

output "topic_arn" {
  description = "ARN del topic de alertas"
  value       = aws_sns_topic.alerts.arn
}

output "alert_email" {
  description = "Email configurado para alertas"
  value       = var.alert_email
  sensitive   = true  # No mostrar en logs
}

# ============================================
# OUTPUTS DE LAMBDA
# ============================================

output "api_lambda_name" {
  description = "Nombre de la Lambda API"
  value       = aws_lambda_function.api.function_name
}

output "checker_lambda_name" {
  description = "Nombre de la Lambda Checker"
  value       = aws_lambda_function.checker.function_name
}

# ============================================
# OUTPUTS DEL SCHEDULER
# ============================================

output "schedule_name" {
  description = "Nombre del schedule"
  value       = aws_scheduler_schedule.checker.name
}

output "check_rate" {
  description = "Frecuencia de chequeo configurada"
  value       = var.check_rate
}