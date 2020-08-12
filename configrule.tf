##############
# Terraform
##############
terraform {
  # minimum allowed version
  required_version = ">= 0.12.20"

  required_providers {
    aws = ">= 2.37.0"
  }
}

#################################################
# AWS Config managed rule for Organization
##################################################

resource "aws_config_organization_managed_rule" "required_tags" {

  name            = "RequiredTags"
  rule_identifier = "REQUIRED_TAGS"

  input_parameters = <<POLICY
{
  "tag1Key": "Product",
  "tag2Key": "Owner",
  "tag3Key": "BusinessUnit",
  "tag4Key": "Environment"
}
POLICY

}

#################################################
# AWS Config managed rule for Organization
##################################################

resource "aws_config_organization_managed_rule" "flow_logs_enabled" {

  name                        = "VPCFlowLogsEnabled"
  rule_identifier             = "VPC_FLOW_LOGS_ENABLED"
  description                 = "Enable VPC flow logs on organization level"
  maximum_execution_frequency = "One_Hour"

  input_parameters = <<POLICY
{
  "trafficType": "ALL"
}
POLICY
}

#################################################
# AWS Config managed rule for Organization
##################################################

resource "aws_config_organization_managed_rule" "ec2_instance_in_vpc" {

  name            = "EC2InstanceInVPC"
  rule_identifier = "INSTANCES_IN_VPC"
  description     = "Checks whether EC2 instances belong to a virtual private cloud (VPC)."

}

#################################################
# AWS Config managed rule for Organization
##################################################

resource "aws_config_organization_managed_rule" "rds_instance_public_access_check" {

  name            = "RDSPublicAccessCheck"
  rule_identifier = "RDS_INSTANCE_PUBLIC_ACCESS_CHECK"
  description     = "Check RDS instances are not publicly accessible"

}

#################################################
# AWS Config managed rule for Organization
##################################################

resource "aws_config_organization_managed_rule" "rds_snapshots_public_prohibited" {

  name            = "RDSSnapshotsPublicProhibited"
  rule_identifier = "RDS_SNAPSHOTS_PUBLIC_PROHIBITED"
  description     = "Check RDS snapshot are not publicly accessible"

}

#################################################
# AWS Config managed rule for Organization
##################################################

resource "aws_config_organization_managed_rule" "check_encrypted_volume" {

  name            = "CheckEncryptedVolumes"
  rule_identifier = "ENCRYPTED_VOLUMES"
  description     = "Check whether the EBS volumes that are in an attached state are encrypted."

}

#################################################
# AWS Config managed rule for Organization
##################################################

resource "aws_config_organization_managed_rule" "ec2_instance_no_public_ip" {

  name            = "EC2InstanceNoPublicIP"
  rule_identifier = "EC2_INSTANCE_NO_PUBLIC_IP"
  description     = "Check EC2 instance does not have an assigned public ip"

}

#################################################
# AWS Config managed rule for Organization 
##################################################

resource "aws_config_organization_managed_rule" "elb_logging_enabled" {

  name            = "ELBLoggingEnabled"
  rule_identifier = "ELB_LOGGING_ENABLED"
  description     = "Check that logging is enabled on load balancer"

}

#################################################
# AWS Config managed rule for Organization
##################################################

resource "aws_config_organization_managed_rule" "rds_storage_encryption_enabled" {

  name            = "RDSStorageEncryption"
  rule_identifier = "RDS_STORAGE_ENCRYPTED"
  description     = "Check that RDS storage is encrypted"

}

#################################################
# AWS Config managed rule for Organization
##################################################

resource "aws_config_organization_managed_rule" "iam_root_access_key_check" {

  name            = "IAMRootAccessKeyCheck"
  rule_identifier = "IAM_ROOT_ACCESS_KEY_CHECK"
  description     = "Checks whether the root user access key is available. The rule is COMPLIANT if the user access key does not exist"

}

#################################################
# AWS Config managed rule for Organization 
##################################################

resource "aws_config_organization_managed_rule" "ebs_snapshot_public_restorable_check" {

  name            = "EBSSnapshotPublicRestorableCheck"
  rule_identifier = "EBS_SNAPSHOT_PUBLIC_RESTORABLE_CHECK"
  description     = "Checks whether Amazon Elastic Block Store snapshots are not publicly restorable. The rule is NON_COMPLIANT if one or more snapshots with the RestorableByUserIds field is set to all. If this field is set to all, then Amazon EBS snapshots are public."

}

#################################################
# AWS Config managed rule for Organization
##################################################

resource "aws_config_organization_managed_rule" "redshift_cluster_public_access_check" {

  name            = "RedshiftClusterPublicAccessCheck"
  rule_identifier = "REDSHIFT_CLUSTER_PUBLIC_ACCESS_CHECK"
  description     = "Checks whether Amazon Redshift clusters are not publicly accessible. The rule is NON_COMPLIANT if the publiclyAccessible field is true in the cluster configuration item."

}

#################################################
# AWS Config managed rule for Organization
##################################################

resource "aws_config_organization_managed_rule" "acm-certificate-expiration-check" {

  name            = "ACMCertificateExpirationCheck"
  rule_identifier = "ACM_CERTIFICATE_EXPIRATION_CHECK"
  description     = "Checks whether ACM Certificates in your account are marked for expiration within 90 days."

  input_parameters = <<POLICY
{
  "daysToExpiration": "90"
}
POLICY
}

#################################################
# AWS Config managed rule for Organization 
##################################################

resource "aws_config_organization_managed_rule" "s3-bucket-public-read-prohibited" {

  name            = "S3BucketPublicReadProhibited"
  rule_identifier = "S3_BUCKET_PUBLIC_READ_PROHIBITED"
  description     = "Checks that your Amazon S3 buckets do not allow public read access. The rule checks the Block Public Access settings, the bucket policy, and the bucket access control list (ACL)."

}

#################################################
# AWS Config managed rule for Organization 
##################################################

resource "aws_config_organization_managed_rule" "s3-bucket-public-write-prohibited" {

  name            = "S3BucketPublicWriteProhibited"
  rule_identifier = "S3_BUCKET_PUBLIC_WRITE_PROHIBITED"
  description     = "Checks that your Amazon S3 buckets do not allow public write access. The rule checks the Block Public Access settings, the bucket policy, and the bucket access control list (ACL)."

}

#################################################
# AWS Config managed rule for Organization 
##################################################

resource "aws_config_organization_managed_rule" "s3-bucket-server-side-encryption-enabled" {

  name            = "S3BucketServerSideEncryptionEnabled"
  rule_identifier = "S3_BUCKET_SERVER_SIDE_ENCRYPTION_ENABLED"
  description     = "Checks that your Amazon S3 bucket either has Amazon S3 default encryption enabled or that the S3 bucket policy explicitly denies put-object requests without server side encryption."

}

#################################################
# AWS Config managed rule for Organization
##################################################

resource "aws_config_organization_managed_rule" "s3-bucket-ssl-requests-only" {

  name            = "S3BucketSSLRequestsOnly"
  rule_identifier = "S3_BUCKET_SSL_REQUESTS_ONLY"
  description     = "Checks whether S3 buckets have policies that require requests to use Secure Socket Layer (SSL)."

}

#################################################
# AWS Config managed rule for Organization
##################################################

resource "aws_config_organization_managed_rule" "restricted-incoming-traffic-common-ports" {

  name            = "RestrictedCommonPorts"
  rule_identifier = "RESTRICTED_INCOMING_TRAFFIC"
  description     = "Checks if the security groups in use do not allow unrestricted incoming TCP traffic to the specified ports. The rule is COMPLIANT when IP addresses of the incoming SSH traffic in the security group are restricted to specified ports."
  input_parameters = <<POLICY
{
  "blockedPort1": "20",
  "blockedPort2": "21",
  "blockedPort3": "3389"
}
POLICY

}

#################################################
# AWS Config managed rule for Organization
##################################################

resource "aws_config_organization_managed_rule" "vpc-sg-open-only-to-authorized-ports" {

  name            = "VPCSecurityGroupOpenOnlyToAuthorizedPorts"
  rule_identifier = "VPC_SG_OPEN_ONLY_TO_AUTHORIZED_PORTS"
  description     = "Checks whether the security group with 0.0.0.0/0 of any Amazon VPC allows only specific inbound TCP or UDP traffic. The rule is NON_COMPLIANT if a security group with inbound 0.0.0.0/0. with no ports provided in the parameters."
  input_parameters = <<POLICY
{
  "authorizedTcpPorts": "443,80"
}
POLICY

}

##################################################
# AWS Config managed rule for Organization 
##################################################

resource "aws_config_organization_managed_rule" "vpc-vpn-2-tunnels-up" {

  name            = "VpcVpn2TunnelsIp"
  rule_identifier = "VPC_VPN_2_TUNNELS_UP"
  description     = "Checks that both AWS Virtual Private Network tunnels provided by AWS Site-to-Site VPN are in UP status. The rule returns NON_COMPLIANT if one or both tunnels are in DOWN status."

}

#################################################
# AWS Config managed rule for Organization
##################################################

resource "aws_config_organization_managed_rule" "access-keys-rotated" {

  name            = "AccessKeysRotated"
  rule_identifier = "ACCESS_KEYS_ROTATED"
  description     = "Checks whether the active access keys are rotated within the number of days specified in maxAccessKeyAge. The rule is NON_COMPLIANT if the access keys have not been rotated for more than maxAccessKeyAge number of days."
  input_parameters = <<POLICY
{
  "maxAccessKeyAge": "90"
}
POLICY

}
##################################################
# AWS Config managed rule for Organization 
##################################################

resource "aws_config_organization_managed_rule" "vpc-default-security-group-closed" {

  name            = "VpcDefaultSecurityGroupClosed"
  rule_identifier = "VPC_DEFAULT_SECURITY_GROUP_CLOSED"
  description     = "Checks the default security grp of any VPC does not allow inbound or outbound traffic. The rule is NON_COMPLIANT if the default security group has one or more inbound or outbound traffic."

}

##################################################
# AWS Config managed rule for Organization 
##################################################

resource "aws_config_organization_managed_rule" "restricted-ssh" {

  name            = "IncomingSSHDisabled"
  rule_identifier = "INCOMING_SSH_DISABLED"
  description     = "Checks whether the incoming SSH traffic for the security groups is accessible. The rule is COMPLIANT when IP addresses of the incoming SSH traffic in the security groups are restricted. This rule applies only to IPv4."

}

#################################################
# AWS Config managed rule for Organization
##################################################

resource "aws_config_organization_managed_rule" "multi-region-cloud-trail-enabled" {

  name            = "MultiRegionCloudTrailEnabled"
  rule_identifier = "MULTI_REGION_CLOUD_TRAIL_ENABLED"
  description     = "Checks that there is at least one multi-region AWS CloudTrail. The rule is NON_COMPLIANT if the trails do not match inputs parameters."
  input_parameters = <<POLICY
{
  "readWriteType": "ALL",
  "s3BucketName": "wellsky-prod-org-cloudtrail"
}
POLICY
}
