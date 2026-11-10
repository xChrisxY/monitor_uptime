resource "aws_scheduler_schedule" "checker" {
  name = "${var.project_name}-schedule"
  description = "Ejecuta el checker cada 5 minutos"
  
  # Los schedules vienen en grupos.
  # El grupo "default" viene con la cuenta
  group_name = "default"

  # Expresión de programación
  schedule_expression = var.check_rate
  schedule_expression_timezone = "UTC"


  # Ventana de tiempo flexible (OFF = puntual)
  # AWS puede ejecutar el schedule dentro de una ventana de tiempo en lugar de puntualmente
  flexible_time_window {
    mode = "OFF"
  }

  # Target: La Lambda Checker
  target {
    arn = aws_lambda_function.checker.arn
    role_arn = aws_iam_role.scheduler.arn

    # Payload que recibe la Lambda
    input = jsonencode({
      source = "scheduler"
      schedule = "${var.project_name}-schedule"
    })

    # Reintentos si falla
    retry_policy {
      # Cuánto tiempo intenta entregar el evento
      maximum_event_age_in_seconds = 60
      # Cuántas veces reintenta si falla
      maximum_retry_attempts = 2
    }

  }

  state = "ENABLED"
}