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