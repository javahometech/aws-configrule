import json
import re
import boto3
from botocore.exceptions import ClientError

RULE_NAME_REGEX = '-(.*?)-'
ses_client = boto3.client('ses', region_name="us-east-1")
config_client = boto3.client('config')

# Read rule_info.json file
ruleinfo_data = json.load(open('rule_info.json', 'r'))

# Lambda handler function
def lambda_handler(event, context):
    # pylint: disable=unused-argument
    generate_reports()

def is_prod_environment():
    """Returns True if running in dev environment otherwise False"""
    return False
    # return 'HOME' in os.environ and os.environ.get('ENVIRONMENT') == 'PROD'

# This is the main function that retrieves the data and emails the reports
def generate_reports():
    aggregators = get_aggregator_data('BusinessUnit')
    print('Got list of BU aggregators')
    for aggregator in aggregators:
        agg_rules_obj = {}
        agg_rules_obj['BusinessUnit'] = get_aggregator_business_unit(aggregator)
        agg_rules_obj['AggregatorName'] = aggregator['AggregatorName']
        agg_rules_obj['AggregatorRules'] = []
        resources_by_rule_name = {}

        for rule in aggregator['AggregatorRules']:
            try:
                base_rule_name = re.findall(RULE_NAME_REGEX, rule['ConfigRuleName'])[0]
            except IndexError:
                continue # Name doesn't match regex, skip this iteration of the for loop
            rule_resources = resources_by_rule_name.get(base_rule_name, [])
            paginator = config_client.get_paginator('get_aggregate_compliance_details_by_config_rule')

            for page in paginator.paginate(
                    ConfigurationAggregatorName=aggregator['AggregatorName'],
                    ConfigRuleName=rule['ConfigRuleName'],
                    ComplianceType='NON_COMPLIANT',
                    AccountId=rule['AccountId'],
                    AwsRegion=rule['AwsRegion']):

                for eval_result in page['AggregateEvaluationResults']:
                    result = eval_result['EvaluationResultIdentifier']['EvaluationResultQualifier']
                    result['AccountId'] = rule['AccountId']
                    result['AwsRegion'] = rule['AwsRegion']
                    rule_resources.append(result)
            resources_by_rule_name[base_rule_name] = rule_resources
        for rule in resources_by_rule_name:
            rule_data = {'rule': rule, 'resources': resources_by_rule_name[rule]}
            if rule in ruleinfo_data:
                rule_data.update(ruleinfo_data[rule])
                agg_rules_obj['AggregatorRules'].append(rule_data)
        agg_rules_obj['AggregatorRules'].sort(key=lambda r: {'High': 0, 'Medium': 1, 'Low': 2}[r['severity']])
        print(f"Sending report for {get_aggregator_business_unit(aggregator)}")
        send_email(aggregator, json.dumps(agg_rules_obj))
        print(f"Sent report for {get_aggregator_business_unit(aggregator)}")
        break

def get_aggregator_data(aggregator_level):
    """
    Parameters:
    aggregatorLevel (string): filter by either Pillar or BusinessUnit.

    Returns a list of aggregators and their rules that were evaluated as non compliant
    """
    aggregator_rule_list = []
    aggregators = get_aggregators()

    for aggregator in aggregators:
        config_rules = []
        aggregator_name = aggregator['AggregatorName']
        tags = aggregator['Tags']

        if tags['AggregateLevel'] != aggregator_level:
            continue

        aggregator_info = {}
        aggregator_info['AggregatorName'] = aggregator_name
        aggregator_info['Tags'] = tags

        paginator = config_client.get_paginator('describe_aggregate_compliance_by_config_rules')
        for page in paginator.paginate(ConfigurationAggregatorName=aggregator_name, Filters={'ComplianceType': 'NON_COMPLIANT'}):
            config_rules.extend(page['AggregateComplianceByConfigRules'])

        aggregator_info['AggregatorRules'] = config_rules
        aggregator_rule_list.append(aggregator_info)
    return aggregator_rule_list

# This function returns a list of aggregators and their tags.
def get_aggregators():
    """Returns a list of AWS Config rule aggregators"""
    aggregators = []
    for page in config_client.get_paginator('describe_configuration_aggregators').paginate():
        for aggregator in page['ConfigurationAggregators']:
            name = aggregator['ConfigurationAggregatorName']
            aggregator_arn = aggregator['ConfigurationAggregatorArn']
            tags = get_tags_for_resource(aggregator_arn)
            aggregators.append({'AggregatorName': name, 'Tags': tags})
    return aggregators

# Returns the tags for a resource
def get_tags_for_resource(arn):
    """Parameters:
    arn (string): The arn of the resource
    """
    resp = config_client.list_tags_for_resource(ResourceArn=arn)
    tags = {tags['Key']: tags['Value'] for tags in resp['Tags']}
    return tags

# Gets the contact address associated with an aggregator
def get_aggregator_email_contact(aggregator):
    if is_prod_environment():
        return aggregator['Tags']['DevOpsContact']
    return DEBUG_EMAIL_DESTINATION

# Gets aggregator BU
def get_aggregator_business_unit(aggregator):
    return aggregator['Tags']['BusinessUnit']

# This functions sends an email using SES templates
def send_email(aggregator, json_data):
    # Try to send the email to test.
    try:
        # Provide the contents of the email.
        to_email = get_aggregator_email_contact(aggregator)
        response = ses_client.send_templated_email(
            Source=AUDIT_EMAIL_ADDRESS,
            SourceArn=SES_SOURCE_ARN,
            ReturnPathArn=SES_RETURNPATH_ARN,
            ReplyToAddresses=[DEV_OPS_DL],
            Destination={
                'ToAddresses': [
                    to_email,
                ],
            },
            Template='AWSConfigComplianceReport',
            TemplateData=json_data
        )
        print(response)
    # Display an error if something goes wrong
    except ClientError as client_error:
        # TODO: Need to report this to the team so they are aware
        print(client_error.response['Error']['Message'])
    else:
        print("Email sent!")
        print("Message ID:" + response['ResponseMetadata']['RequestId'])
