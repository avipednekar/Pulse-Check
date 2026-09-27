variable "aws_region" {
  description = "AWS region used for all PulseCheck infrastructure."
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Project tag applied to all AWS resources."
  type        = string
  default     = "PulseCheck"
}
