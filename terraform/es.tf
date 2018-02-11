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
    security_group_ids = ["sg-b9aec5ce"]
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
  name        = "elasticsearch"
  description = "for elasticsearch"
  vpc_id      = "${var.vpc_id}"

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
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
