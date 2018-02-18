resource "aws_iam_instance_profile" "deeplearning_trainer" {
  name = "deeplearning-trainer-${var.name}"
  role = "${aws_iam_role.deeplearning_trainer.name}"
}

resource "aws_iam_role_policy" "deeplearning_bucket_access" {
  name = "deeplearning-bucket-access"
  role = "${aws_iam_role.deeplearning_trainer.id}"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:ListAllMyBuckets",
            "Resource": "arn:aws:s3:::*"
        },
        {
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::${var.bucket_name}",
                "arn:aws:s3:::${var.bucket_name}/*"
            ]
        }
    ]
}
EOF
}

resource "aws_iam_role" "deeplearning_trainer" {
  name = "deeplearning-trainer-${var.name}"
  path = "/"

  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Principal": {
               "Service": "ec2.amazonaws.com"
            },
            "Effect": "Allow",
            "Sid": ""
        }
    ]
}
EOF
}

data "aws_ami" "deeplearning" {
  most_recent = true

  filter {
    name   = "name"
    values = ["Deep Learning AMI*Ubuntu*Version 4.0"]
  }
}

#
data "template_file" "init" {
  template = "${file("${path.module}/init.sh.tmpl")}"

  vars {
    DATASET_S3_PATH = "${var.dataset_s3_path}"
    NETWORK         = "${var.network}"
    DATASHAPE       = "${var.datashape}"
  }
}

data "template_file" "sync_and_remove" {
  template = "${file("${path.module}/sync-and-remove.sh.tmpl")}"

  vars {
    OUTPUT_S3_PATH = "${var.output_s3_path}"
  }
}

resource "aws_spot_instance_request" "dl" {
  ami       = "${data.aws_ami.deeplearning.id}"
  spot_type = "one-time"

  #instance_type        = "p3.2xlarge"
  instance_type          = "p2.xlarge"
  spot_price             = "0.5"
  wait_for_fulfillment   = true
  key_name               = "${var.keyname}"
  iam_instance_profile   = "${aws_iam_instance_profile.deeplearning_trainer.name}"
  vpc_security_group_ids = ["${var.security_group}"]
  subnet_id              = "${var.subnet}"

  root_block_device {
    volume_size           = "75"
    delete_on_termination = true
  }

  tags {
    Name = "dl-${var.name}"
  }

  connection {
    user        = "ubuntu"
    private_key = "${file("/home/tomas/.ssh/id_rsa")}"
    host        = "${aws_spot_instance_request.dl.public_ip}"
  }

  provisioner "file" {
    content     = "${data.template_file.init.rendered}"
    destination = "/home/ubuntu/init.sh"
  }

  provisioner "file" {
    content     = "${data.template_file.sync_and_remove.rendered}"
    destination = "/home/ubuntu/sync-and-remove.sh"
  }

  provisioner "remote-exec" {
    inline = [
      "chmod +x /home/ubuntu/init.sh",
      "chmod +x /home/ubuntu/sync-and-remove.sh",
      "/home/ubuntu/init.sh",
      "crontab -l | { cat; echo \"* * * * * /home/ubuntu/sync-and-remove.sh\"; } | crontab -",
    ]
  }

  # todo open stats and metrics
}
