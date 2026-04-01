variable "aws_region"         { type = string, default = "us-east-1" }
variable "project_name"       { type = string, default = "agentic-devops" }
variable "environment"        { type = string, default = "dev" }
variable "vpc_cidr"           { type = string, default = "10.0.0.0/16" }
variable "availability_zones" { type = list(string) }
variable "public_subnets"     { type = list(string) }
variable "cluster_version"    { type = string, default = "1.29" }
variable "node_instance_type" { type = string, default = "t3.micro" }
variable "node_desired"       { type = number, default = 1 }
variable "node_min"           { type = number, default = 1 }
variable "node_max"           { type = number, default = 2 }
