provider "aws" {
    region = "us-east-1"
}

variable "name" {
    description = "Name the instance on deploy"
}

resource "aws_instance" "devops_jenkins" {
    ami = "ami-0747bdcabd34c712a"
    instance_type = "t2.micro"
    key_name = "devops"

    tags = {
        Name = "${var.name}"
    }
}