resource "aws_dynamodb_table" "monitors" {
  name         = "${var.project_name}-monitors"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  # Solo definimos los atributos que son keys
  # Los demás atributos se crean dinámicamente
  attribute {
    name = "id"
    type = "S"
  }

  # Protección contra borrado accidental (en prod sería true)
  deletion_protection_enabled = false

  tags = {
    Name = "${var.project_name}-monitors"
  }
}