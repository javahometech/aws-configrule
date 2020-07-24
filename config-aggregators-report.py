import boto3

config = boto3.client('config')

def lambda_handler(event,context):
    get_resources()

def get_resources():
    config_rules = get_config_rules()
    rules = []
    final_resp = []
    for config_rule in config_rules:
        aggregator_name = config_rule['AggregatorName']
        aggregator_rules = config_rule['AggregatorRules']
        agg_rules_obj  = {}
        agg_rules_obj['AggregatorName'] = aggregator_name

        for rule in aggregator_rules:
            resource_dict  = {}
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
                resource_dict = resource['EvaluationResultIdentifier']['EvaluationResultQualifier']
                resource_dict['AccountId'] = account_id
                resource_dict['AwsRegion'] = aws_region
                rules.append(resource_dict)
            agg_rules_obj['AggregatorRules'] = rules
        final_resp.append(agg_rules_obj)
    print(final_resp)

def get_config_rules():
    aggregator_names = get_aggregator_names()
    config_rule_names = []
    aggregator_name_rules = []
    for aggregator_name in aggregator_names:
        aggregator_name_rule = {}
        aggregator_name_rule['AggregatorName'] = aggregator_name
        config_rules_resp = config.describe_aggregate_compliance_by_config_rules(
            ConfigurationAggregatorName = aggregator_name,
            Filters={
                'ComplianceType': 'NON_COMPLIANT'
            }
        )
        for config_rule in config_rules_resp['AggregateComplianceByConfigRules']:
            del config_rule['Compliance']
            config_rule_names.append(config_rule)
        
        while 'NextToken' in config_rules_resp:
            config_rules_resp = config.describe_aggregate_compliance_by_config_rules(
            ConfigurationAggregatorName = aggregator_name,
                Filters={
                    'ComplianceType': 'NON_COMPLIANT'
                },
                NextToken = config_rules_resp['NextToken']
            )
            for config_rule in config_rules_resp['AggregateComplianceByConfigRules']:
                del config_rule['Compliance']
                config_rule_names.append(config_rule)
        aggregator_name_rule['AggregatorRules'] = config_rule_names
        aggregator_name_rules.append(aggregator_name_rule)
    return aggregator_name_rules

def get_aggregator_names():
    response = config.describe_configuration_aggregators()
    aggregator_names = []
    for aggregator in response['ConfigurationAggregators']:
        aggregator_name = aggregator['ConfigurationAggregatorName']
        aggregator_names.append(aggregator_name)
    
    while 'NextToken' in response:
        response = config.describe_configuration_aggregators(
            NextToken = response['NextToken']
        )
        for aggregator in response['ConfigurationAggregators']:
            aggregator_name = aggregator['ConfigurationAggregatorName']
            aggregator_names.append(aggregator_name)
    return aggregator_names

# lambda_handler(None,None)
