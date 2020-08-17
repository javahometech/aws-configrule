import json
import re
import boto3
from botocore.exceptions import ClientError

RULE_NAME_REGEX = '-(.*?)-'
ses_client = boto3.client('ses', region_name="us-east-1")
config_client = boto3.client('config')


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
    """
    This method is used to generate_reports
    """
    with open('rule_info.json', 'r') as fp:
        ruleinfo_data = json.load(fp)

    aggregators = get_aggregator_data('BusinessUnit')
    print('Got list of BU aggregators')
    for aggregator in aggregators:
        agg_rules_obj = {}
        agg_rules_obj['BusinessUnit'] = get_aggregator_business_unit(
            aggregator)
        agg_rules_obj['AggregatorName'] = aggregator['AggregatorName']
        agg_rules_obj['AggregatorRules'] = []
        resources_by_rule_name = {}

        for rule in aggregator['AggregatorRules']:
            if re.findall(RULE_NAME_REGEX, rule['ConfigRuleName']) != []:
                base_rule_name = re.findall(RULE_NAME_REGEX,
                                            rule['ConfigRuleName'])[0]
            rule_resources = resources_by_rule_name.get(base_rule_name, [])
            paginator = CONFIG_CLIENT.get_paginator(\
                'get_aggregate_compliance_details_by_config_rule')

            for page in paginator.paginate(
                    ConfigurationAggregatorName=aggregator['AggregatorName'],
                    ConfigRuleName=rule['ConfigRuleName'],
                    ComplianceType='NON_COMPLIANT',
                    AccountId=rule['AccountId'],
                    AwsRegion=rule['AwsRegion']):

                for eval_result in page['AggregateEvaluationResults']:
                    result = eval_result['EvaluationResultIdentifier'][
                        'EvaluationResultQualifier']
                    result['AccountId'] = rule['AccountId']
                    result['AwsRegion'] = rule['AwsRegion']
                    rule_resources.append(result)
            resources_by_rule_name[base_rule_name] = rule_resources
        medium_arr = []
        low_arr = []
        for rule in resources_by_rule_name:
            rule_data = {
                'rule': rule,
                'resources': resources_by_rule_name[rule]
            }
            if rule in ruleinfo_data:
                rule_data.update(ruleinfo_data[rule])
                severity = ruleinfo_data[rule]['severity']
                agg_rules_obj['AggregatorRules'].append(rule_data)

        agg_rules_obj['AggregatorRules'].sort(
            key=lambda x: numeric_severity(severity))
        # agg_rules_obj['AggregatorRules'].extend(medium_arr)
        # agg_rules_obj['AggregatorRules'].extend(low_arr)
        # print(json.dumps(agg_rules_obj))

def numeric_severity(severity):
    return {"Low": 0, "Medium": 1, "High": 2}[severity]


"""
def appending_rule_data(agg_rules_obj):
    with open('rule_info.json', 'r') as fp:
        ruleinfo_data = json.load(fp)

    for agg_rule in agg_rules_obj['AggregatorRules']:
        for rule_name, value_data in ruleinfo_data.items():
#            print(value_data)
            if agg_rule['rule'] == rule_name:
                for key, value in value_data.items():
                    print(value)
                    agg_rule[key] = value
    return json.dumps(agg_rules_obj)
"""


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

        paginator = config_client.get_paginator(
            'describe_aggregate_compliance_by_config_rules')
        for page in paginator.paginate(
                ConfigurationAggregatorName=aggregator_name,
                Filters={'ComplianceType': 'NON_COMPLIANT'}):
            config_rules.extend(page['AggregateComplianceByConfigRules'])

        aggregator_info['AggregatorRules'] = config_rules
        aggregator_rule_list.append(aggregator_info)
    return aggregator_rule_list


# This function returns a list of aggregators and their tags.
def get_aggregators():
    """Returns a list of AWS Config rule aggregators"""
    aggregators = []
    for page in config_client.get_paginator(
            'describe_configuration_aggregators').paginate():
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
