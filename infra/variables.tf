# Variables de configuración inicial
variable "aws_region" {
  description = "Región de AWS donde crear los recursos"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Prefijo para nombrar todos los recursos"
  type        = string
  default     = "uptime"
}

# Variables de alertas
variable "alert_email" {
  description = "Dirección de email para recibir alertas de caídas"
  type        = string
  default     = "christopheryahirm@gmail.com"
}

# variables de comportamiento
variable "failure_threshold" {
  description = "Número de fallos consecutivos antes de declarar un sitio caído"
  type        = number
  default     = 2

  validation {
    condition     = var.failure_threshold >= 1 && var.failure_threshold <= 10
    error_message = "failure_threshold debe estar entre 1 y 10"
  }

}

variable "check_rate" {
  description = "Frecuencia de revisión (expresión de rate de EventBridge)"
  type        = string
  default     = "rate(5 minutes)"
}


# Variables de límites

# Límite de cuántos sitios puedes monitorear
variable "max_monitors" {
  description = "Número máximo de monitores permitidos"
  type        = number
  default     = 20
}

variable "request_timeout_seconds" {
  description = "Timeout para las peticiones HTTP del checker"
  type        = number
  default     = 5
}