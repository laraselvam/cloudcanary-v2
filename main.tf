provider "aws" {
  region = "ap-southeast-2"
}

resource "aws_instance" "cloudcanary_vm" {
  ami           = "ami-0aa3edce488471086"
  instance_type = "t3.micro"

  tags = {
    Name = "CloudCanary-Best-Region"
  }
}
