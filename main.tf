# Description of Lambda Function
resource "aws_lambda_function" "lambda_dx" {
  function_name     = "DXMetricReport"
  handler           = "lambda_dx_report.lambda_handler"
  runtime           = "python3.8"
  role              = aws_iam_role.lambda_exec.arn
  filename          = "./lambda_dx_report.zip"
  source_code_hash  = filebase64sha256("./lambda_dx_report.zip")

  # Configure CloudWatch Logs
  environment {
    variables = {
      "LOG_GROUP_NAME" = "/aws/lambda/DXMetricReport"  # CloudWatch Log group name
    }
  }
}

# CloudWatch Logs group for Lambda function logs
resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/DXMetricReport"  # CloudWatch Log group name
  retention_in_days = 7  # Retain logs for 7 days, adjust as needed
}

# IAM Resources
resource "aws_iam_role" "lambda_exec" {
  name = "lambda_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Effect = "Allow"
      },
    ]
  })
}

resource "aws_iam_policy" "lambda_policy" {
  name        = "lambda_metrics_policy"
  description = "IAM policy for accessing CloudWatch and SNS from Lambda"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "cloudwatch:GetMetricData",
          "cloudwatch:GetMetricWidgetImage",
          "sns:Publish"
        ],
        Resource = "*"
        Effect = "Allow"
      },
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "arn:aws:logs:*:*:*"
        Effect = "Allow"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attach" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# Trigger Lambda Function
resource "aws_cloudwatch_event_rule" "every_week" {
  name                = "every-hour"
  schedule_expression = "rate(1 hour)"
  state = "DISABLED"
}

resource "aws_cloudwatch_event_target" "invoke_lambda" {
  rule      = aws_cloudwatch_event_rule.every_week.name
  target_id = "TargetFunction"
  arn       = aws_lambda_function.lambda_dx.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_dx.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.every_week.arn  # Corrected reference
}
