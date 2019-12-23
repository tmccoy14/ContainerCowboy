import argparse
import boto3
import datetime
from datetime import date, timedelta
import xlwt
from xlwt import Workbook

"""
This script uses boto3, the AWS SDK for Python, to obtain your account cost information for a certain
time period. The script creates a Cost Explorer client that allows you to get the costs for each of the 
services that your AWS account is using. It then formats the data and creates an excel spread sheet that 
contains the formatted data.
"""

# Create the Cost Explorer Client
costExplorer = boto3.client("ce")

# create required method parameters
today = date.today()
start_date = today - timedelta(days=30)

resultsByTime = []

token = None

while True:
    if token:
        kwargs = {"NextPageToken": token}
    else:
        kwargs = {}

    # retrieves cost and usage metrics for account
    costUsageReport = costExplorer.get_cost_and_usage(
        TimePeriod={"Start": str(start_date), "End": str(today)},
        Granularity="DAILY",
        Metrics=["BlendedCost",],
        GroupBy=[
            {"Type": "DIMENSION", "Key": "LINKED_ACCOUNT"},
            {"Type": "DIMENSION", "Key": "SERVICE"},
        ],
    )

    # add each response to a list
    resultsByTime += costUsageReport["ResultsByTime"]
    token = costUsageReport.get("NextPageToken")
    if not token:
        break

# create excel workbook to export data to
wb = Workbook()
sheet = wb.add_sheet("Sheet 1")
style = xlwt.easyxf("font: bold 1")

# create excel sheet headers
sheet.write(0, 0, "Time Period", style)
sheet.write(0, 1, "Service", style)
sheet.write(0, 2, "Amount", style)

totalAmount = 0

i = 1
# iterate over the resources and assign them to be written to the file by service
for results in resultsByTime:
    for group in results["Groups"]:
        currentDate = results["TimePeriod"]["Start"]
        serviceName = group["Keys"][1]

        amount = group["Metrics"]["BlendedCost"]["Amount"]
        amount = float(amount)
        amount = round(amount, 2)
        finalServiceAmount = "$" + str(amount)
        totalAmount += amount

        sheet.write(i, 0, currentDate)
        sheet.write(i, 1, serviceName)
        sheet.write(i, 2, finalServiceAmount)
        i += 1

# write the total amount of costs for the current date to the file
totalAmount = round(totalAmount, 2)
totalAmount = "$" + str(totalAmount)

sheet.write(i, 0, "Total", style)
sheet.write(i, 2, totalAmount, xlwt.easyxf("pattern: pattern solid, fore_color yellow"))

# after all data has been written to excel sheet save the workbook
excelName = "CostAndUsageReport " + str(start_date) + "_" + str(today) + ".xls"
wb.save(excelName)

# create s3 client
s3 = boto3.client("s3")

bucket_name = "studio-cost-and-usage-reports"

# upload file to the bucket
s3.upload_file(excelName, bucket_name, "reports/{}".format(excelName))