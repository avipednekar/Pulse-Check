output "ec2_public_ip" {
  description = "Public IP address of the PulseCheck EC2 instance."
  value       = aws_instance.pulsecheck_app.public_ip
}

output "ec2_public_dns" {
  description = "Public DNS name of the PulseCheck EC2 instance."
  value       = aws_instance.pulsecheck_app.public_dns
}

output "rds_endpoint" {
  description = "PostgreSQL endpoint"
  value       = aws_db_instance.pulsecheck.endpoint
}

output "rds_database_name" {
  value = aws_db_instance.pulsecheck.db_name
}

output "sns_topic_arn" {
  description = "ARN of the SNS topic for CloudWatch alarms"
  value       = aws_sns_topic.alerts.arn
}

output "cloudwatch_cpu_alarm_name" {
  description = "Name of the EC2 High CPU CloudWatch alarm"
  value       = aws_cloudwatch_metric_alarm.ec2_cpu_high.alarm_name
}