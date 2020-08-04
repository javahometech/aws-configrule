
import boto3
import json
import os
from jinja2 import Template
config = boto3.client('config')
ses_client = boto3.client('ses')

# Lambda handler function. 

def lambda_handler(event,context):
    get_resources()

# Function to get resources id, resource type, account id, region from get aggregate compliance details by config rule method
# This function get/prints the resource id, type, account id, region in json format.

def get_resources():
    aggregators = get_aggregator_data()
    rules = []
    final_resp = []
    for aggregator in aggregators:
        rules = []
        aggregator_name = aggregator['AggregatorName']
        aggregator_rules = aggregator['AggregatorRules']
        agg_rules_obj  = {}
        agg_rules_obj['AggregatorName'] = aggregator_name

        for rule in aggregator_rules:
            result  = {}
            rule_name = rule['ConfigRuleName']
            account_id = rule['AccountId']
            aws_region = rule['AwsRegion']
            rule_resp = config.get_aggregate_compliance_details_by_config_rule(
                ConfigurationAggregatorName = aggregator_name,
                ConfigRuleName = rule_name,
                ComplianceType = 'NON_COMPLIANT',
                AccountId = account_id,
                AwsRegion = aws_region
            )
            for resource in rule_resp['AggregateEvaluationResults']:
                result = resource['EvaluationResultIdentifier']['EvaluationResultQualifier']
                result['AccountId'] = account_id
                result['AwsRegion'] = aws_region
                rules.append(result)
            agg_rules_obj['AggregatorRules'] = rules
        final_resp.append(agg_rules_obj)
        # send_email(str(agg_rules_obj),get_to_email_id(aggregator_name))
    render_template_send_email(final_resp)
    # print(json.dumps(final_resp))

# Function gets aggregator data based out of get_aggregator_names function.
# This function returns aggregator rule list. 

def get_aggregator_data():
    aggregator_names = get_aggregator_names()
    config_rules = [] # Change 
    aggregator_rule_list = []
    
    for aggregator_name in aggregator_names:
        aggregator_rule_info = {}
        aggregator_rule_info['AggregatorName'] = aggregator_name
        next_token = ''
        while True:
            config_rules_resp = config.describe_aggregate_compliance_by_config_rules(
            ConfigurationAggregatorName = aggregator_name,
                Filters={
                    'ComplianceType': 'NON_COMPLIANT'
                },
                NextToken = next_token
            )
            config_rules += config_rules_resp['AggregateComplianceByConfigRules']
            if 'NextToken' in config_rules_resp:
                next_token = config_rules_resp['NextToken']
            else:
                break 
        aggregator_rule_info['AggregatorRules'] = config_rules
        aggregator_rule_list.append(aggregator_rule_info)
   
    return aggregator_rule_list

# Function to get aggregator names page by page. 
# The describe_configuration_aggregator returns details of one or more configuration aggregators associated with the account

def get_aggregator_names():
    aggregator_names = []
    for page in config.get_paginator('describe_configuration_aggregators').paginate():
        aggregator_names += [agg['ConfigurationAggregatorName'] for agg in page['ConfigurationAggregators']]
    return aggregator_names

def get_to_email_id(aggregator_name):
    resp = config.describe_configuration_aggregators(
        ConfigurationAggregatorNames = [aggregator_name]
    )
    aggregator_arn = resp['ConfigurationAggregators'][0]['ConfigurationAggregatorArn']
    resp = config.list_tags_for_resource(
        ResourceArn=aggregator_arn
    )
    for tag in resp['Tags']:
        if tag['Key'] == 'Email':
            return tag['Value']

# Send Email 
def send_email(body):
    from_email = 'hari.kammana@gmail.com'
    subject = 'Aggrigators Report'
    to_email = 'hari.kammana@gmail.com'
    ses_client.send_email(
     Source=from_email,
     Destination = {
         'ToAddresses': [
            to_email,
        ]
    },
    Message = {
        'Subject': {
            'Data': subject,
            'Charset': 'UTF-8'
        },
        'Body': {
            'Html': {
                'Data': body,
                'Charset': 'UTF-8'
            }
        }
    },
    )

def render_template_send_email(aggregators):
    with open('aggregators-report.j2', 'r') as aggr_file:
        template = Template(aggr_file.read())
        rendered_template = template.render(
            aggregators=aggregators
        )
        print('Rendered ', rendered_template)
        send_email(rendered_template)
lambda_handler(None,None)
# send_email()
