# Sensitive Variables

variable "db_username" {
  description = "PostgreSQL master username"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "PostgreSQL master password"
  type        = string
  sensitive   = true
}

# PostgreSQL RDS Instance

resource "aws_db_instance" "pulsecheck" {
  identifier = "pulsecheck-db"

  engine         = "postgres"
  engine_version = "18"

  instance_class = "db.t4g.micro"

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp3"

  db_name  = "pulsecheck"
  username = var.db_username
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.rds_subnet_group.name
  vpc_security_group_ids = [aws_security_group.pulsecheck_db_sg.id]

  publicly_accessible = false

  multi_az            = false
  storage_encrypted   = true
  skip_final_snapshot = true

  backup_retention_period = 1

  tags = {
    Name = "pulsecheck-db"
  }
}