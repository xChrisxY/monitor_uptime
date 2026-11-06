# SNS TOPIC
resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-alerts"
  display_name = "Uptime Alerts"

  tags = {
    Name = "${var.project_name}-alerts"
  }

}

# SUSCRIPCIÓN DE EMAIL
resource "aws_sns_topic_subscription" "email" { 
  topic_arn = aws_sns_topic.alerts.arn
  protocol = "email"
  endpoint = var.alert_email

  # La suscripción requiere confirmación manual
}
