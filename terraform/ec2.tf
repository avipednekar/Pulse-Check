# Get latest Amazon Linux 2023 AMI

data "aws_ami" "amazon_linux_2023" {
  most_recent = true

  owners = ["137112412989"] # Amazon

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

# SSH Key Pair
# Replace with the path to your public key

resource "aws_key_pair" "pulsecheck_key" {
  key_name   = "pulsecheck-key"
  public_key = file(pathexpand("~/.ssh/pulsecheck.pub"))
}

# IAM Role for EC2

resource "aws_iam_role" "ec2_ecr_role" {
  name = "pulsecheck-ec2-ecr-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

# Allow ECR Pull Access

resource "aws_iam_role_policy_attachment" "ecr_readonly" {
  role       = aws_iam_role.ec2_ecr_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

# Allow SSM access (deploy via HTTPS instead of SSH)
resource "aws_iam_role_policy_attachment" "ssm_managed" {
  role       = aws_iam_role.ec2_ecr_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "pulsecheck-ec2-profile"
  role = aws_iam_role.ec2_ecr_role.name
}

# EC2 Instance

resource "aws_instance" "pulsecheck_app" {
  ami                    = data.aws_ami.amazon_linux_2023.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.pulsecheck_app_sg.id]

  associate_public_ip_address = true

  key_name = aws_key_pair.pulsecheck_key.key_name

  iam_instance_profile = aws_iam_instance_profile.ec2_profile.name

  user_data = <<-EOF
              #!/bin/bash
              dnf update -y

              dnf install -y docker

              systemctl enable docker
              systemctl start docker

              usermod -aG docker ec2-user
              EOF

  # Prevent Terraform from destroying and recreating the instance
  # when AWS publishes a new AMI or user_data formatting changes
  lifecycle {
    ignore_changes = [ami, user_data]
  }

  tags = {
    Name = "pulsecheck-app"
  }
}

# Elastic IP — permanent static IP that survives instance replacement
resource "aws_eip" "pulsecheck_eip" {
  instance = aws_instance.pulsecheck_app.id
  domain   = "vpc"

  tags = {
    Name = "pulsecheck-eip"
  }
}