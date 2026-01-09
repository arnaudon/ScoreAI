# Define required providers
terraform {
  # Ensure the use of a compatible Terraform version
  required_version = ">= 0.14.0"
  required_providers {
    # Define OpenStack terraform provider
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 2.0.0"# (1)!
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Configure the OpenStack Provider
provider "openstack" {
  cloud = "PCP-KP6YXB3-dc3-a" 
}

resource "openstack_compute_keypair_v2" "my_keypair" {
  name       = "my_keypair"
  public_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPVhHNMLPAhEVb4wuulkTF4knQp7lohVmi8GP6MGeH3f alexisarnaudon@alexiss-MBP"
}

# Define the security group
resource "openstack_networking_secgroup_v2" "my_security_group" {
  name                 = "my_security_group"
  description          = "My neutron security group"
  # We want our security group to be fully managed by Terraform
  delete_default_rules = true # (1)!
}

# Add SSH rule to our security group
resource "openstack_networking_secgroup_rule_v2" "my_sg_ssh" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "0.0.0.0/0"
  # Link the rule to our security group
  security_group_id = openstack_networking_secgroup_v2.my_security_group.id
}

# Allow HTTP
resource "openstack_networking_secgroup_rule_v2" "my_sg_ssh_http" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 80
  port_range_max    = 80
  remote_ip_prefix  = "0.0.0.0/0"
  # Link the rule to our security group
  security_group_id = openstack_networking_secgroup_v2.my_security_group.id
}

resource "openstack_networking_secgroup_rule_v2" "backend" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 8000
  port_range_max    = 8000
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.my_security_group.id
}
# Allow HTTPs
resource "openstack_networking_secgroup_rule_v2" "my_sg_ssh_https" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 443
  port_range_max    = 443
  remote_ip_prefix  = "0.0.0.0/0"
  # Link the rule to our security group
  security_group_id = openstack_networking_secgroup_v2.my_security_group.id
}

# This rule allows the server to send traffic OUT to the world (IPv4)
resource "openstack_networking_secgroup_rule_v2" "egress_v4" {
  direction         = "egress"
  ethertype         = "IPv4"
  security_group_id = openstack_networking_secgroup_v2.my_security_group.id
}

# This rule allows the server to send traffic OUT to the world (IPv6)
resource "openstack_networking_secgroup_rule_v2" "egress_v6" {
  direction         = "egress"
  ethertype         = "IPv6"
  security_group_id = openstack_networking_secgroup_v2.my_security_group.id
}
# Create a web server resource
resource "openstack_compute_instance_v2" "my_webserver" {
  name            = "web-server"
  image_name      = "Debian 12 bookworm"
  flavor_name     = "a1-ram2-disk80-perf1"
  key_pair        = openstack_compute_keypair_v2.my_keypair.name
  security_groups = [openstack_networking_secgroup_v2.my_security_group.name]

  network {
    name          = "ext-net1"
  }
  user_data = file("./setup.sh")
}


provider "aws" {
  # Infomaniak Credentials
  access_key = "798a99de91f84745b1ef757d2eb62447"
  secret_key = "405f903d221744b6ad6be4658119d380"
  region     = "us-east-1" # Or your specific Infomaniak region

  # Redirect AWS provider to Infomaniak
  endpoints {
    s3 = "https://s3.pub1.infomaniak.cloud"
  }

  # Required for compatibility with non-AWS S3 providers
  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_region_validation      = true
  s3_use_path_style           = true
}

# Create the Bucket
resource "aws_s3_bucket" "test_bucket" {
  bucket = "test_bucket"
}

# Optional: Set Bucket to Private
# resource "aws_s3_bucket_acl" "example" {
#   bucket = aws_s3_bucket.my_infomaniak_bucket.id
#   acl    = "private"
# }
