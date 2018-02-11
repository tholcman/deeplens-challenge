/*
# just local state
terraform {
  backend "s3" {
    bucket               = "none"
    key                  = "exercise-counter"
    region               = "eu-west-1"
    dynamodb_table       = "terraform_locking"
    workspace_key_prefix = "workspace"
  }
}

*/

provider "aws" {
  region              = "us-east-1"
  allowed_account_ids = ["935232462890"]
  profile             = "personal"
}
