# ROL PARA LAMBDA API

# Trust policy: quién puede asumir este rol
data "aws_iam_policy_document" "lambda_assume_role" {

  statement {
    effect = "Allow"

    principals {
      type = "Service"
      identifiers = [ "lambda.amazonaws.com" ]
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

resource "aws_iam_role_policy" "api_lambda" {
  name = "${var.project_name}-api-policy"
  role = aws_iam_role.api_lambda.id 
  policy = data.aws_iam_policy_document.api_lambda_permissions.json
}

# Permisos para escribir logs (política gestionada por AWS)
resource "aws_iam_role_policy_attachment" "api_lambda_logs" {
  role       = aws_iam_role.api_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}


# ROL PARA LAMBDA CHECKER
resource "aws_iam_role" "checker_lambda" {
  name = "${var.project_name}-checker-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

data "aws_iam_policy_document" "checker_lambda_permissions" {

  # Permisos para DynamoDB (solo lectura y actualización)
  statement {
    effect = "Allow"
    actions = [ 
      "dynamodb:Scan",
      "dynamodb:UpdateItem"
    ]
    resources = [ aws_dynamodb_table.monitors.arn ]
  }

  # Permisos para publicar en SNS
  statement {
    effect = "Allow"
    actions = [ "sns:Publish" ]
    resources = [ aws_sns_topic.alerts.arn ]
  }
}

resource "aws_iam_role_policy" "checker_lambda" {
  name = "${var.project_name}-checker-policy"
  role = aws_iam_role.checker_lambda.id
  policy = data.aws_iam_policy_document.checker_lambda_permissions.json
}

resource "aws_iam_role_policy_attachment" "checker_lambda_logs" {
  role       = aws_iam_role.checker_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}


# ROL PARA EVENTBRIDGE SCHEDULER
data "aws_iam_policy_document" "scheduler_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["scheduler.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "scheduler" {
  name               = "${var.project_name}-scheduler-role"
  assume_role_policy = data.aws_iam_policy_document.scheduler_assume_role.json
}

data "aws_iam_policy_document" "scheduler_permissions" {
  statement {
    effect    = "Allow"
    actions   = ["lambda:InvokeFunction"]
    resources = [aws_lambda_function.checker.arn]
  }
}

resource "aws_iam_role_policy" "scheduler" {
  name   = "${var.project_name}-scheduler-policy"
  role   = aws_iam_role.scheduler.id
  policy = data.aws_iam_policy_document.scheduler_permissions.json
}