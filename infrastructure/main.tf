terraform {
  required_version = ">= 1.6.0"
  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 2.0.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket                      = "scoreguide-tfstate"
    key                         = "infrastructure/terraform.tfstate"
    region                      = "us-east-1"
    endpoints                   = { s3 = "https://s3.pub1.infomaniak.cloud" }
    skip_credentials_validation = true
    skip_region_validation      = true
    skip_requesting_account_id  = true
    skip_metadata_api_check     = true
    use_path_style              = true
    skip_s3_checksum            = true
  }
}

provider "openstack" {
  cloud = "PCP-KP6YXB3-dc3-a"
}

# Infomaniak S3 via the AWS provider.
# Credentials read from AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY env vars.
provider "aws" {
  region = "us-east-1"

  endpoints {
    s3 = "https://s3.pub1.infomaniak.cloud"
  }

  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_region_validation      = true
  s3_use_path_style           = true
}

resource "openstack_compute_keypair_v2" "my_keypair" {
  name       = "my_keypair"
  public_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPVhHNMLPAhEVb4wuulkTF4knQp7lohVmi8GP6MGeH3f alexisarnaudon@alexiss-MBP"
}

resource "openstack_networking_secgroup_v2" "my_security_group" {
  name                 = "my_security_group"
  description          = "Web server security group (managed by Terraform)"
  delete_default_rules = true
}

resource "openstack_networking_secgroup_rule_v2" "ssh_ingress" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.my_security_group.id
}

resource "openstack_networking_secgroup_rule_v2" "http_ingress" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 80
  port_range_max    = 80
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.my_security_group.id
}

resource "openstack_networking_secgroup_rule_v2" "https_ingress" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 443
  port_range_max    = 443
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.my_security_group.id
}

resource "openstack_networking_secgroup_rule_v2" "egress_v4" {
  direction         = "egress"
  ethertype         = "IPv4"
  security_group_id = openstack_networking_secgroup_v2.my_security_group.id
}

resource "openstack_networking_secgroup_rule_v2" "egress_v6" {
  direction         = "egress"
  ethertype         = "IPv6"
  security_group_id = openstack_networking_secgroup_v2.my_security_group.id
}

# State-only renames — no API calls, just retitle existing resources in state.
moved {
  from = openstack_networking_secgroup_rule_v2.my_sg_ssh
  to   = openstack_networking_secgroup_rule_v2.ssh_ingress
}

moved {
  from = openstack_networking_secgroup_rule_v2.my_sg_ssh_http
  to   = openstack_networking_secgroup_rule_v2.http_ingress
}

moved {
  from = openstack_networking_secgroup_rule_v2.my_sg_ssh_https
  to   = openstack_networking_secgroup_rule_v2.https_ingress
}

resource "openstack_compute_instance_v2" "my_webserver" {
  name            = "web-server"
  image_name      = "Debian 12 bookworm"
  flavor_name     = "a2-ram4-disk80-perf1"
  key_pair        = openstack_compute_keypair_v2.my_keypair.name
  security_groups = [openstack_networking_secgroup_v2.my_security_group.name]

  network {
    name = "ext-net1"
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [image_name]
  }
}

resource "aws_s3_bucket" "scoreguide" {
  bucket = "scoreguide"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket" "tfstate" {
  bucket = "scoreguide-tfstate"

  lifecycle {
    prevent_destroy = true
  }
}

output "vm_ipv4" {
  value = openstack_compute_instance_v2.my_webserver.access_ip_v4
}

output "vm_ipv6" {
  value = openstack_compute_instance_v2.my_webserver.access_ip_v6
}

output "app_bucket" {
  value = aws_s3_bucket.scoreguide.bucket
}

output "tfstate_bucket" {
  value = aws_s3_bucket.tfstate.bucket
}
