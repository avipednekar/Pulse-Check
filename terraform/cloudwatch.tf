# ------------------------------------------------------------------------------
# SNS Topic for Alarms and Notifications
# ------------------------------------------------------------------------------

variable "alert_email" {
  description = "Email address to receive CloudWatch alarm notifications (leave empty to skip email subscription)"
  type        = string
  default     = ""
}

resource "aws_sns_topic" "alerts" {
  name = "pulsecheck-alerts"

  tags = {
    Name = "pulsecheck-alerts"
  }
}

resource "aws_sns_topic_subscription" "email_subscription" {
  count     = var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# ------------------------------------------------------------------------------
# CloudWatch Alarm: EC2 High CPU Utilization (> 80%)
# ------------------------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "ec2_cpu_high" {
  alarm_name          = "pulsecheck-ec2-cpu-high"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "Triggered when EC2 CPU utilization exceeds 80% for two consecutive 5-minute periods."
  actions_enabled     = true

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]

  dimensions = {
    InstanceId = aws_instance.pulsecheck_app.id
  }

  tags = {
    Name = "pulsecheck-ec2-cpu-high"
  }
}

# ------------------------------------------------------------------------------
# CloudWatch Alarm: EC2 Status Check Failed
# ------------------------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "ec2_status_check_failed" {
  alarm_name          = "pulsecheck-ec2-status-check-failed"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "StatusCheckFailed"
  namespace           = "AWS/EC2"
  period              = 60
  statistic           = "Maximum"
  threshold           = 0
  alarm_description   = "Triggered when EC2 instance or system status check fails for 2 consecutive minutes."
  actions_enabled     = true

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]

  dimensions = {
    InstanceId = aws_instance.pulsecheck_app.id
  }

  tags = {
    Name = "pulsecheck-ec2-status-check-failed"
  }
}
