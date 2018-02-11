resource "aws_elasticsearch_domain" "count-exercise" {
  domain_name           = "count-exercise"
  elasticsearch_version = "5.5"

  cluster_config {
    instance_type = "t2.small.elasticsearch"
  }

  advanced_options {
    "rest.action.multi.allow_explicit_index" = "true"
  }

  vpc_options {
    subnet_ids         = ["subnet-32ea8d1d"]
    security_group_ids = ["${aws_security_group.elasticsearch.id}"]
  }

  access_policies = <<CONFIG
{
    "Version":"2012-10-17",
    "Statement":[
        {
            "Action":"es:*",
            "Effect":"Allow",
            "Principal":{"AWS":"*"},
            "Resource":"arn:aws:es:us-east-1:935232462890:domain/count-exercise/*"
        }
    ]
}
CONFIG
}

resource "aws_security_group" "elasticsearch" {
  name_prefix = "elasticsearch-"
  description = "for elasticsearch shared "
  vpc_id      = "${var.vpc_id}"

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group_rule" "allow_elasticsearch" {
  type              = "ingress"
  from_port         = 9200
  to_port           = 9300
  protocol          = "tcp"
  cidr_blocks       = ["172.30.0.0/16", "212.4.134.24/32"]
  security_group_id = "${aws_security_group.elasticsearch.id}"
}

resource "aws_security_group_rule" "allow_http" {
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  cidr_blocks       = ["172.30.0.0/16", "212.4.134.24/32"]
  security_group_id = "${aws_security_group.elasticsearch.id}"
}

resource "aws_security_group_rule" "allow_https" {
  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = ["172.30.0.0/16", "212.4.134.24/32"]
  security_group_id = "${aws_security_group.elasticsearch.id}"
}

resource "aws_security_group_rule" "allow_ssh" {
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = ["172.30.0.0/16", "212.4.134.24/32"]
  security_group_id = "${aws_security_group.elasticsearch.id}"
}

resource "aws_instance" "proxy" {
  ami                    = "ami-66506c1c"                             // ubuntu 16.04
  instance_type          = "t2.nano"
  key_name               = "th-xps-13"
  vpc_security_group_ids = ["${aws_security_group.elasticsearch.id}"]
  subnet_id              = "subnet-32ea8d1d"

  tags {
    Name = "es-proxy"
  }
}
