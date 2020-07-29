import boto3
import json
config = boto3.client('config')
ses_client = boto3.client('ses')
def lambda_handler(event,context):
    get_resources()

def get_resources():
    aggregators = get_config_rules()
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
        send_email(str(agg_rules_obj))
    json.dumps(final_resp)
    print(final_resp)


def get_config_rules():
    aggregator_names = get_aggregator_names()
    config_rule_names = []
    aggregator_rule_info = []
    
    for aggregator_name in aggregator_names:
        aggregator_name_rule = {}
        aggregator_name_rule['AggregatorName'] = aggregator_name
        next_token = ''
        while True:
            config_rules_resp = config.describe_aggregate_compliance_by_config_rules(
            ConfigurationAggregatorName = aggregator_name,
                Filters={
                    'ComplianceType': 'NON_COMPLIANT'
                },
                NextToken = next_token
            )
            config_rule_names += config_rules_resp['AggregateComplianceByConfigRules']
            if 'NextToken' in config_rules_resp:
                next_token = config_rules_resp['NextToken']
            else:
                break 
        aggregator_name_rule['AggregatorRules'] = config_rule_names
        aggregator_rule_info.append(aggregator_name_rule)
    return aggregator_rule_info

'''
def get_aggregator_names():
    aggregator_names = []
    next_token = ''

    while True:
        response = config.describe_configuration_aggregators(
            NextToken = next_token
        )
        aggregator_names += [aggregator['ConfigurationAggregatorName'] for aggregator in response['ConfigurationAggregators']]
        if 'NextToken' in response:
            next_token = response['NextToken']
        else:
            break
    return aggregator_names

'''
# The above code which is comented is replaced with code below 

def get_aggregator_names():
    aggregator_names = []
    for page in config.get_paginator('describe_configuration_aggregators').paginate():
        aggregator_names += [agg['ConfigurationAggregatorName'] for agg in page['ConfigurationAggregators']]
    return aggregator_names

def get_emil_ids():
    pass

def send_email(body):

    ses_client.send_email(
     Source='hari.kammana@gmail.com',
     Destination = {
         'ToAddresses': [
            'hari.kammana@gmail.com',
        ]
    },
    Message = {
        'Subject': {
            'Data': 'Demo Report',
            'Charset': 'UTF-8'
        },
        'Body': {
            'Text': {
                'Data': body,
                'Charset': 'UTF-8'
            }
        }
    },
    )
# lambda_handler(None,None)
