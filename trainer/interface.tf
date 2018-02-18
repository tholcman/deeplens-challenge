variable "name" {
  description = "Name of trainer. Will be part of all names created by this TF"
}

variable "bucket_name" {
  description = "Bucket to allow spot instance in"
}

variable "dataset_s3_path" {
  description = "Will be synced to data/ so should contain train.rec and val.rec"
}

variable "output_s3_path" {
  description = "nohup.out and model/* will be synced here"
}

variable "network" {
  description = "inceptionv3|resnet50|vgg16_reduced|resnet101"
}

variable "datashape" {
  default     = 224
  description = "Size of input network. 300 for vgg16_reduced"
}

/*
variable "vpc_id" {
  description = "VPC id to run everything in."
}
*/
variable "subnet" {
  description = "Subnet"
}

variable "security_group" {
  description = "security group"
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
