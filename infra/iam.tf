# ROL PARA LAMBDA API

# Trust policy: quién puede asumir este rol
data "aws_iam_policy_document" "lambda_assume_role" {

  statement {
    effect = "Allow"

    principals {
      type = "Service"
      identifiers = [ "lambda:amazonaws.com" ]
    }

    actions = [ "sts:AssumeRole" ]
  }

}

# El rol
resource "aws_iam_role" "api_lambda" {
  name = "${var.project_name}-api-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

# Permisos: qué puede hacer
data "aws_iam_policy_document" "api_lambda_permissions" {
  
  # Permisos para DynamoDB
  statement {
    effect = "Allow"
    actions = [ 
      "dynamodb:PutItem",
      "dynamodb:GetItem",
      "dynamodb:Scan",
      "dynamodb:UpdateItem",
      "dynamodb:DeleteItem",
    ] 
    resources = [ aws_dynamodb_table.monitors.arn ]
  }
}

# Permisos para escribir logs (política gestionada por AWS)
resource "aws_iam_role_policy_attachment" "api_lambda_logs" {
  role       = aws_iam_role.api_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}