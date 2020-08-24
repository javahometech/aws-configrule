#!/usr/bin/python
#%%
import boto3
import json
from json2html import *

# Create SES client
ses = boto3.client('ses')

# Read the json data file
#file = open("data.json", "r")
file = open("jsonNewData.json", "r")
#file = open("tagJsonData.json", "r")
jsondata = file.read()
print(jsondata)

# Read html file which has json rendering
html_file = open("index.html", "r")
#html_file = open("compliance-report.html", "r")
htmldata = html_file.read()
print(htmldata)
#%%
#BusinessUnit = "BloodWork "
#BusinessUnit = BusinessUnit + " AWS Accounts Compliance Report"
# Update SES template
response = ses.update_template(
    Template={
        'TemplateName': 'AWSConfigComplianceReport',
        'SubjectPart': '{{BusinessUnit}} AWS Accounts Compliance Report',
        # 'SubjectPart': BusinessUnit,
        'TextPart': 'Non Compliance Aggregator ',
        'HtmlPart': htmldata
    }
)
print("Updated the template ...")
print(response)
#%%
# Send email using a template
response = ses.send_templated_email(
    Source='indukuriv@gmail.com',
    Destination={
        'ToAddresses': [
            'indukuriv@gmail.com',
        ],
    },
    Template='AWSConfigComplianceReport',
    TemplateData=jsondata
)
print("Sent email ...")
print(response)
