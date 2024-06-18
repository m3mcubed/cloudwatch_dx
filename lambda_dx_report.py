import boto3
import datetime
import json
import logging
import base64

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create a CloudWatch and SNS client
cloudwatch = boto3.client('cloudwatch')
sns = boto3.client('sns')

def lambda_handler(event, context):
    logger.info("Starting Lambda function")

    # Define the time period for the report
    end_time = datetime.datetime.now(datetime.timezone.utc)
    start_time = end_time - datetime.timedelta(days=7)

    # Define the widget for the combined graph
    widget = {
        "width": 800,
        "height": 600,
        "start": start_time.isoformat(),
        "end": end_time.isoformat(),
        "metrics": [
            ["DX", "VirtualInterfacePpsIngress", "ConnectionId", "dxcon-fg4kumqm", "VirtualInterfaceId", "dxvif-fgfcmngk"],
            [ ".", "VirtualInterfacePpsEgress", "ConnectionId", "dxcon-fg4kumqm", "VirtualInterfaceId", "dxvif-fgfcmngk"],
            [ ".", "VirtualInterfaceBpsIngress", "ConnectionId", "dxcon-fg4kumqm", "VirtualInterfaceId", "dxvif-fgfcmngk"],
            [ ".", "VirtualInterfaceBpsEgress", "ConnectionId", "dxcon-fg4kumqm", "VirtualInterfaceId", "dxvif-fgfcmngk"],
            [ ".", "VirtualInterfacePpsIngress", "ConnectionId", "dxcon-fgqihqb2", "VirtualInterfaceId", "dxvif-fgq7t21s"],
            [ ".", "VirtualInterfacePpsEgress", "ConnectionId", "dxcon-fgqihqb2", "VirtualInterfaceId", "dxvif-fgq7t21s"],
            [ ".", "VirtualInterfaceBpsIngress", "ConnectionId", "dxcon-fgqihqb2", "VirtualInterfaceId", "dxvif-fgq7t21s"],
            [ ".", "VirtualInterfaceBpsEgress", "ConnectionId", "dxcon-fgqihqb2", "VirtualInterfaceId", "dxvif-fgq7t21s"]
        ],
        "period": 300,
        "stat": "Average",
        "title": "Virtual Interface Metrics",
        "yAxis": {
            "left": {
                "label": "Packets/Bytes",
                "showUnits": False
            }
        }
    }

    try:
        response = cloudwatch.get_metric_widget_image(
            MetricWidget=json.dumps(widget)
        )
        image_data = base64.b64encode(response['MetricWidgetImage']).decode('utf-8')

        logger.info("Successfully fetched combined graph for Virtual Interface Metrics")
    except Exception as e:
        logger.error(f"Error fetching graph for Virtual Interface Metrics: {e}")
        return {
            'statusCode': 500,
            'body': f"Error fetching graph: {e}"
        }

    report_content = f"DX Metrics Report:\n\n![Graph](data:image/png;base64,{image_data})\n"

    # Send report via SNS
    try:
        sns_response = sns.publish(
            TopicArn='arn:aws:sns:us-east-1:176436512199:DX_Alarms',
            Message=report_content,
            Subject='DX Metrics Report',
            MessageAttributes={
                'ContentType': {
                    'DataType': 'String',
                    'StringValue': 'text/html'
                }
            }
        )
        logger.info("Successfully sent report via SNS")
    except Exception as e:
        logger.error(f"Error sending report via SNS: {e}")
        return {
            'statusCode': 500,
            'body': 'Error sending report via SNS'
        }
    
    return {
        'statusCode': 200,
        'body': 'Report generated and sent successfully'
    }
