"""
lambda.py
"""
import json
import re
import boto3
# from botocore.exceptions import ClientError

RULE_NAME_REGEX = '-(.*?)-'
SES_CLIENT = boto3.client('ses', region_name="us-east-1")
CONFIG_CLIENT = boto3.client('config')

# Lambda handler function

def lambda_handler(event, context):
    """
    lambda_handler
    """
    # pylint: disable=unused-argument
    generate_reports()

def is_prod_environment():
    """Returns True if running in dev environment otherwise False"""
    return False
    # return 'HOME' in os.environ and os.environ.get('ENVIRONMENT') == 'PROD'

# This is the main function that retrieves the data and emails the reports

def generate_reports():
    """
    This method is used to generate_reports
    """
    with open('rule_info.json', 'r') as file_data:
        ruleinfo_data = json.load(file_data)

    #aggregators = get_aggregator_data('BusinessUnit')
    #print('Got list of BU aggregators')
    for aggregator in get_aggregator_data('BusinessUnit'):
        agg_rules_obj = {}
        agg_rules_obj['BusinessUnit'] = get_aggregator_business_unit(aggregator)
        agg_rules_obj['AggregatorName'] = aggregator['AggregatorName']
        agg_rules_obj['AggregatorRules'] = []
        resources_by_rule_name = {}

        for rule in aggregator['AggregatorRules']:
            #rule_name = rule['ConfigRuleName']
            #account_id = rule['AccountId']
            #aws_region = rule['AwsRegion']
            if re.findall(RULE_NAME_REGEX, rule['ConfigRuleName']) != []:
                base_rule_name = re.findall(RULE_NAME_REGEX, rule['ConfigRuleName'])[0]
            rule_resources = resources_by_rule_name.get(base_rule_name, [])
            paginator = CONFIG_CLIENT.get_paginator(\
                'get_aggregate_compliance_details_by_config_rule')

            for page in paginator.paginate(ConfigurationAggregatorName=aggregator['AggregatorName'],
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
        # medium_arr = []
        # low_arr = []
        for rule in resources_by_rule_name:
            rule_data = {'rule': rule, 'resources': resources_by_rule_name[rule]}
            rule_info = ruleinfo_data[rule]
            rule_data.update(rule_info)
            agg_rules_obj['AggregatorRules'].append(rule_data)
            sorted(agg_rules_obj['AggregatorRules'], key=lambda i: i['severity'])
        print(json.dumps(agg_rules_obj))

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

        paginator = CONFIG_CLIENT.get_paginator('describe_aggregate_compliance_by_config_rules')
        for page in paginator.paginate(\
        ConfigurationAggregatorName=aggregator_name, Filters={'ComplianceType': 'NON_COMPLIANT'}):
            config_rules.extend(page['AggregateComplianceByConfigRules'])

        aggregator_info['AggregatorRules'] = config_rules
        aggregator_rule_list.append(aggregator_info)
    return aggregator_rule_list

# This function returns a list of aggregators and their tags.
def get_aggregators():
    """Returns a list of AWS Config rule aggregators"""
    aggregators = []
    for page in CONFIG_CLIENT.get_paginator('describe_configuration_aggregators').paginate():
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
    resp = CONFIG_CLIENT.list_tags_for_resource(ResourceArn=arn)
    tags = {tags['Key']: tags['Value'] for tags in resp['Tags']}
    return tags

# Gets the contact address associated with an aggregator
def get_aggregator_email_contact(aggregator):
    """
    get_aggregator_email_contact
    """
    if is_prod_environment():
        return aggregator['Tags']['DevOpsContact']
    # return DEBUG_EMAIL_DESTINATION
    return None

# Gets aggregator BU
def get_aggregator_business_unit(aggregator):
    """
    get_aggregator_business_unit
    """
    return aggregator['Tags']['BusinessUnit']
