# Elastic Container Registry (ECR)

resource "aws_ecr_repository" "pulsecheck" {
  name                 = "pulsecheck"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "pulsecheck"
  }
}

output "ecr_repository_url" {
  description = "ECR Repository URL"
  value       = aws_ecr_repository.pulsecheck.repository_url
}