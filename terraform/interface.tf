variable "vpc_id" {
  description = "VPC id to run everything in."
}

variable "subnet" {
  description = "Subnet where to start ES and proxy"
}

variable "keyname" {
  description = "SSH keypair name to use one EC2 proxy"
}

variable "profile" {
  description = "Which profile from ~/.aws/credentials use"
}

variable "allowed_account_id" {
  description = "Account id ... to avoid mistakes"
}
