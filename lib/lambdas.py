"""
    https://docs.aws.amazon.com/lambda/latest/dg/monitoring-metrics.html
"""

from grafanalib.core import (
    Alert,
    AlertCondition,
    Dashboard,
    Graph,
    GreaterThan,
    GridPos,
    Logs,
    MILLISECONDS_FORMAT,
    OP_AND,
    RTYPE_MAX,
    single_y_axis,
    SHORT_FORMAT,
    Stat,
    TimeRange,
    Row,
    Target,
    YAxes,
    YAxis,
)
from grafanalib.cloudwatch import CloudwatchMetricsTarget, CloudwatchLogsInsightsTarget

from lib.annotations import get_release_annotations
from lib.commons import (
    ALERT_REF_ID,
    ALERT_THRESHOLD,
    EDITABLE,
    SHARED_CROSSHAIR,
    TIMEZONE,
    TRANSPARENT,
)
from lib.sns import create_sns_graph
from lib.templating import get_release_templating
from lib import colors

from typing import List

NAMESPACE = "AWS/Lambda"
LAMBDA_DASHBOARD_PREFIX = "Lambda: "


MINIMUM_ALIAS = "Min"
AVERAGE_ALIAS = "Avg"
MAXIMUM_ALIAS = "Max"
LAMBDA_INVOCATIONS_ALIAS = "Invocations"
LAMBDA_ERRORS_ALIAS = "Errors"


def dispatcher(service, trigger, *args, **kwargs):
    """
    lambda dashboard generator
    """

    if service != "lambda":
        raise Exception("Lambda dispatcher recieved a non lambda call")

    dispatch = {
        "cognito-idp": lambda_cognito_dashboard,
        "cloudwatch-event-schedule": lambda_cron_dashboard,
        "cloudwatch-event-trigger": lambda_events_dashboard,
        "cloudwatch-logs": lambda_cron_dashboard,
        "sqs": lambda_sqs_dashboard,
        "sns": lambda_sns_sqs_dashboard,
        "null": lambda_basic_dashboard,
    }

    return dispatch[trigger](**kwargs)


def lambda_generate_invocation_graphs(
    name: str, cloudwatch_data_source: str, lambda_insights_namespace: str, notifications: List[str], *args, **kwargs
):
    return [
        lambda_generate_invocations_graph(name, cloudwatch_data_source, notifications=notifications),
        lambda_generate_duration_graph(name, cloudwatch_data_source, notifications=notifications),
    ]

def lambda_generate_memory_utilization_graphs(
    name: str, cloudwatch_data_source: str, lambda_insights_namespace: str, notifications: List[str], *args, **kwargs
):
    return [
        lambda_generate_memory_utilization_percentage_graph(name, cloudwatch_data_source, lambda_insights_namespace, notifications=notifications),
        lambda_generate_maximum_memory_stat(name, cloudwatch_data_source, lambda_insights_namespace)
    ]


def lambda_generate_logs_panel(name: str, cloudwatch_data_source: str) -> Logs:
    """
    Generate Logs panel
    """
    targets = [
        CloudwatchLogsInsightsTarget(
            expression="fields @timestamp, @xrayTraceId, @message | filter @message like /^(?!.*(START|END|REPORT|LOGS|EXTENSION)).*$/ | sort @timestamp desc",
            logGroupNames = ["/aws/lambda/{}".format(name)]
        ),
    ]

    return Logs(
        title="Logs",
        dataSource=cloudwatch_data_source,
        targets=targets,
        wrapLogMessages=True,
        prettifyLogMessage=True,
        enableLogDetails=True,
        # gridPos=GridPos(8,24,0,0)
    )

def lambda_generate_memory_utilization_percentage_graph(
    name: str, cloudwatch_data_source: str, lambda_insights_namespace: str, notifications: List[str], *args, **kwargs
) -> Graph:
    """
    Generate lambda graph
    """

    targets = [
        CloudwatchMetricsTarget(
            alias=MINIMUM_ALIAS,
            namespace=lambda_insights_namespace,
            statistics=["Minimum"],
            metricName="memory_utilization",
            dimensions={"function_name": name},
        ),
        CloudwatchMetricsTarget(
            alias=AVERAGE_ALIAS,
            namespace=lambda_insights_namespace,
            statistics=["Average"],
            metricName="memory_utilization",
            dimensions={"function_name": name},
            refId=ALERT_REF_ID
        ),
        CloudwatchMetricsTarget(
            alias=MAXIMUM_ALIAS,
            namespace=lambda_insights_namespace,
            statistics=["Maximum"],
            metricName="memory_utilization",
            dimensions={"function_name": name},
        ),
    ]

    yAxes = YAxes(
        YAxis(format=SHORT_FORMAT, decimals=2),
        YAxis(format=SHORT_FORMAT, decimals=2),
    )

    seriesOverrides = [
        {"alias": MINIMUM_ALIAS, "color": "#C8F2C2", "lines": False},
        {"alias": AVERAGE_ALIAS, "color": "#FADE2A", "fill": 0},
        {
            "alias": MAXIMUM_ALIAS,
            "color": "rgb(77, 159, 179)",
            "fillBelowTo": MINIMUM_ALIAS,
            "lines": False,
        },
    ]

    alert = None

    # https://docs.aws.amazon.com/lambda/latest/dg/monitoring-metrics.html
    if notifications:
        alert = Alert(
            name="{} Memory utilization Errors".format(name),
            message="{} is having Memory utilization errors".format(name),
            executionErrorState="alerting",
            alertConditions=[
                AlertCondition(
                    Target(refId=ALERT_REF_ID),
                    timeRange=TimeRange("5m", "now"),
                    evaluator=GreaterThan(90),
                    reducerType=RTYPE_MAX,
                    operator=OP_AND,
                )
            ],
            gracePeriod="1m",
            notifications=notifications,
        )

    return Graph(
        title="Lambda Memory Utilization Percentage",
        dataSource=cloudwatch_data_source,
        targets=targets,
        seriesOverrides=seriesOverrides,
        yAxes=yAxes,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        alert=alert,
        alertThreshold=ALERT_THRESHOLD,
        # gridPos=GridPos(8,12,0,0)
    ).auto_ref_ids()

def lambda_generate_memory_utilization_graph(
    name: str, cloudwatch_data_source: str, lambda_insights_namespace: str, *args, **kwargs
) -> Graph:
    """
    Generate lambda graph
    """

    targets = [
        CloudwatchMetricsTarget(
            alias="used_memory_max",
            namespace=lambda_insights_namespace,
            statistics=["Maximum"],
            metricName="used_memory_max",
            dimensions={"function_name": name},
        ),
        CloudwatchMetricsTarget(
            alias="allocated_memory",
            namespace=lambda_insights_namespace,
            statistics=["Maximum"],
            metricName="total_memory",
            dimensions={"function_name": name},
        ),
    ]

    yAxes = YAxes(
        YAxis(format="decmbytes"),
    )

    seriesOverrides = [
        {
            "alias": "used_memory_max",
            "points": False,
            "color": colors.GREEN,
        },
        {
            "alias": "allocated_memory",
            "points": False,
            "color": colors.RED,
            "fill": 0
        },
    ]

    alert = None

    return Graph(
        title="Lambda Memory Utilization",
        dataSource=cloudwatch_data_source,
        targets=targets,
        seriesOverrides=seriesOverrides,
        yAxes=yAxes,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        alert=alert,
        alertThreshold=ALERT_THRESHOLD,
        # gridPos=GridPos(8,12,12,0)
    ).auto_ref_ids()

def lambda_generate_duration_graph(
    name: str, cloudwatch_data_source: str, *args, **kwargs
) -> Graph:
    """
    Generate lambda graph
    """

    targets = [
        CloudwatchMetricsTarget(
            alias=MINIMUM_ALIAS,
            namespace=NAMESPACE,
            statistics=["Minimum"],
            metricName="Duration",
            dimensions={"FunctionName": name},
        ),
        CloudwatchMetricsTarget(
            alias=AVERAGE_ALIAS,
            namespace=NAMESPACE,
            statistics=["Average"],
            metricName="Duration",
            dimensions={"FunctionName": name},
        ),
        CloudwatchMetricsTarget(
            alias=MAXIMUM_ALIAS,
            namespace=NAMESPACE,
            statistics=["Maximum"],
            metricName="Duration",
            dimensions={"FunctionName": name},
        )
    ]

    yAxes = YAxes(
        YAxis(format=MILLISECONDS_FORMAT, decimals=2),
        YAxis(format=SHORT_FORMAT, decimals=2),
    )

    seriesOverrides = [
        {"alias": MINIMUM_ALIAS, "color": "#C8F2C2", "lines": False},
        {"alias": AVERAGE_ALIAS, "color": "#FADE2A", "fill": 0},
        {
            "alias": MAXIMUM_ALIAS,
            "color": "rgb(77, 159, 179)",
            "fillBelowTo": MINIMUM_ALIAS,
            "lines": False,
        },
    ]

    alert = None

    return Graph(
        title="Lambda Invocation Duration",
        dataSource=cloudwatch_data_source,
        targets=targets,
        seriesOverrides=seriesOverrides,
        yAxes=yAxes,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        alert=alert,
        alertThreshold=ALERT_THRESHOLD,
        # gridPos=GridPos(8,12,12,0)
    ).auto_ref_ids()


def lambda_generate_maximum_memory_stat(
    name: str, cloudwatch_data_source: str, lambda_insights_namespace: str
) -> Stat:
    """
    Generate lambda graph
    """

    targets = [
        CloudwatchMetricsTarget(
            alias=MAXIMUM_ALIAS,
            namespace=lambda_insights_namespace,
            statistics=["Maximum"],
            metricName="total_memory",
            dimensions={"function_name": name},
        )
    ]

    return Stat(
        title="Lambda Allocated Memory",
        dataSource=cloudwatch_data_source,
        targets=targets,
        transparent=TRANSPARENT,
        format="decmbytes",
        thresholds=[
            {
                "color": "green"
            }
        ],
        editable=EDITABLE,
        # gridPos=GridPos(7,4,20,9)
    )

def lambda_generate_invocations_graph(
    name: str, cloudwatch_data_source: str, notifications: List[str], *args, **kwargs
) -> Graph:
    """
    Generate lambda graph
    """

    targets = [
        CloudwatchMetricsTarget(
            alias=LAMBDA_INVOCATIONS_ALIAS,
            namespace=NAMESPACE,
            statistics=["Sum"],
            metricName="Invocations",
            dimensions={"FunctionName": name},
        ),
        CloudwatchMetricsTarget(
            alias=LAMBDA_ERRORS_ALIAS,
            namespace=NAMESPACE,
            statistics=["Sum"],
            metricName="Errors",
            dimensions={"FunctionName": name},
            refId=ALERT_REF_ID,
        ),
    ]

    yAxes = YAxes(
        YAxis(format=SHORT_FORMAT, decimals=2),
        YAxis(format=SHORT_FORMAT, decimals=2),
    )

    seriesOverrides = [
        {
            "alias": LAMBDA_INVOCATIONS_ALIAS,
            "points": False,
            "color": colors.GREEN,
        },
        {
            "alias": LAMBDA_ERRORS_ALIAS,
            "points": False,
            "color": colors.RED,
        },
    ]

    alert = None

    # https://docs.aws.amazon.com/lambda/latest/dg/monitoring-metrics.html
    if notifications:
        alert = Alert(
            name="{} Invocation Errors".format(name),
            message="{} is having invocation errors".format(name),
            executionErrorState="alerting",
            alertConditions=[
                AlertCondition(
                    Target(refId=ALERT_REF_ID),
                    timeRange=TimeRange("5m", "now"),
                    evaluator=GreaterThan(0),
                    reducerType=RTYPE_MAX,
                    operator=OP_AND,
                )
            ],
            gracePeriod="1m",
            notifications=notifications,
        )

    return Graph(
        title="Lambda Invocations and Errors",
        dataSource=cloudwatch_data_source,
        targets=targets,
        seriesOverrides=seriesOverrides,
        yAxes=yAxes,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        alert=alert,
        alertThreshold=ALERT_THRESHOLD,
        # gridPos=GridPos(8,12,0,0)
    ).auto_ref_ids()


def lambda_cron_dashboard(*args, **kwargs):
    """
    Generate lambda dashboard for cron
    """
    tags = ["cron"]
    return create_lambda_only_dashboard(tags, *args, **kwargs)


def lambda_basic_dashboard(*args, **kwargs):
    """
    Generate lambda dashboard for cron
    """
    tags = []
    return create_lambda_only_dashboard(tags, *args, **kwargs)


def lambda_cognito_dashboard(*args, **kwargs):
    """
    Generate lambda dashboard for Cognito
    """
    tags = ["cognito"]
    return create_lambda_only_dashboard(tags, *args, **kwargs)


def lambda_events_dashboard(*args, **kwargs):
    """
    Generate lambda dashboard for Cloudwatch Events
    """
    tags = ["cloudwatch events"]
    return create_lambda_only_dashboard(tags, *args, **kwargs)


def lambda_logs_dashboard(*args, **kwargs):
    """
    Generate lambda dashboard for Cloudwatch Logs
    """
    tags = ["cloudwatch logs"]
    return create_lambda_only_dashboard(tags, *args, **kwargs)


def create_lambda_only_dashboard(
    tags: List[str],
    name: str,
    cloudwatch_data_source: str,
    influxdb_data_source: str,
    lambda_insights_namespace: str,
    notifications: List[str],
    environment: str,
    *args,
    **kwargs
):
    """Create a dashboard with just the lambda"""

    return Dashboard(
        title="{}{}".format(LAMBDA_DASHBOARD_PREFIX, name),
        editable=EDITABLE,
        annotations=get_release_annotations(influxdb_data_source),
        templating=get_release_templating(influxdb_data_source),
        tags=tags + ["lambda", environment],
        timezone=TIMEZONE,
        sharedCrosshair=SHARED_CROSSHAIR,
        rows=[
            Row(
                panels=[
                    lambda_generate_invocations_graph(name, cloudwatch_data_source, notifications=notifications),
                    lambda_generate_duration_graph(name, cloudwatch_data_source),
                ]
            ),
            Row(
                panels=[
                    lambda_generate_memory_utilization_percentage_graph(name, cloudwatch_data_source, lambda_insights_namespace, notifications=notifications),
                    lambda_generate_memory_utilization_graph(name, cloudwatch_data_source, lambda_insights_namespace),
                ]
            ),
            Row(
                panels=[
                    lambda_generate_logs_panel(name, cloudwatch_data_source),
                ]
            ),
        ]
    ).auto_panel_ids()


def create_lambda_sqs_dlq_graph(
    name: str, cloudwatch_data_source: str, fifo: bool, notifications: List[str]
):
    """Create SQS Deadletter graph"""

    if fifo:
        name += ".fifo"

    targets = [
        CloudwatchMetricsTarget(
            alias="Approximate number of messages available",
            namespace="AWS/SQS",
            period="1m",
            statistics=["Maximum"],
            metricName="ApproximateNumberOfMessagesVisible",
            dimensions={"QueueName": name},
            refId=ALERT_REF_ID if notifications else None,
        )
    ]

    yAxes = single_y_axis(format=SHORT_FORMAT)
    alert = None

    # https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-monitoring-using-cloudwatch.html
    # https://aws.amazon.com/about-aws/whats-new/2019/12/amazon-sqs-now-supports-1-minute-cloudwatch-metrics/
    if notifications:
        alert = Alert(
            name="{} messages".format(name),
            message="{} is having messages".format(name),
            executionErrorState="alerting",
            alertConditions=[
                AlertCondition(
                    Target(refId=ALERT_REF_ID),
                    timeRange=TimeRange("5m", "now"),
                    evaluator=GreaterThan(0),
                    reducerType=RTYPE_MAX,
                    operator=OP_AND,
                ),
            ],
            gracePeriod="5m",
            notifications=notifications,
        )

    return Graph(
        title="SQS Dead Letter Queue: {}".format(name),
        dataSource=cloudwatch_data_source,
        targets=targets,
        yAxes=yAxes,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        alert=alert,
        alertThreshold=ALERT_THRESHOLD,
    ).auto_ref_ids()


def create_lambda_sqs_graph(name: str, cloudwatch_data_source: str, fifo: bool):
    """Create SQS graph"""

    if fifo:
        name += ".fifo"

    targets = [
        CloudwatchMetricsTarget(
            alias="Number of messages sent to the queue",
            namespace="AWS/SQS",
            period="1m",
            statistics=["Sum"],
            metricName="NumberOfMessagesSent",
            dimensions={"QueueName": name},
        )
    ]

    yAxes = single_y_axis(format=SHORT_FORMAT)

    return Graph(
        title="SQS: {}".format(name),
        dataSource=cloudwatch_data_source,
        targets=targets,
        yAxes=yAxes,
        transparent=TRANSPARENT,
        editable=EDITABLE,
    ).auto_ref_ids()


def lambda_sqs_dashboard(
    name: str,
    cloudwatch_data_source: str,
    influxdb_data_source: str,
    lambda_insights_namespace: str,
    notifications: List[str],
    environment: str,
    fifo: bool,
    *args,
    **kwargs
):
    """Create a dashboard with Lambda and its SQS dead letter queue"""
    tags = ["lambda", "sqs", environment]

    if fifo:
        tags += ["fifo"]

    sqs_graph = create_lambda_sqs_graph(
        name=name, cloudwatch_data_source=cloudwatch_data_source, fifo=fifo
    )
    dead_letter_sqs_graph = create_lambda_sqs_dlq_graph(
        name=name + "-dlq",
        cloudwatch_data_source=cloudwatch_data_source,
        fifo=fifo,
        notifications=notifications,
    )

    return Dashboard(
        title="{}{}".format(LAMBDA_DASHBOARD_PREFIX, name),
        editable=EDITABLE,
        annotations=get_release_annotations(influxdb_data_source),
        templating=get_release_templating(influxdb_data_source),
        tags=tags,
        timezone=TIMEZONE,
        sharedCrosshair=SHARED_CROSSHAIR,
        rows=[
            Row(title="Invocations", showTitle=True,
                panels=[
                    lambda_generate_invocations_graph(name, cloudwatch_data_source, notifications=[]),
                    lambda_generate_duration_graph(name, cloudwatch_data_source),
                ]
            ),
            Row(title="Memory utilization", showTitle=True,
                panels=[
                    lambda_generate_memory_utilization_percentage_graph(name, cloudwatch_data_source, lambda_insights_namespace, notifications=notifications),
                    lambda_generate_memory_utilization_graph(name, cloudwatch_data_source, lambda_insights_namespace),
                ]
            ),
            Row(title="Logs", showTitle=True, collapse=True,
                panels=[
                    lambda_generate_logs_panel(name, cloudwatch_data_source),
                ]
            ),
            Row(title="Queues", showTitle=True, panels=[sqs_graph]),
            Row(title="Dead Letter Queues", showTitle=True, panels=[dead_letter_sqs_graph]),
        ]
    ).auto_panel_ids()


def lambda_sns_sqs_dashboard(
    name: str,
    cloudwatch_data_source: str,
    influxdb_data_source: str,
    lambda_insights_namespace: str,
    notifications: List[str],
    environment: str,
    topics: List[str],
    fifo: bool,
):
    """Create a dashboard with Lambda, the SNS topics it is invoked from and its SQS dead letter queue"""
    tags = ["lambda", "sqs", environment, "sns"]

    if fifo:
        tags += ["fifo"]

    sqs_graph = create_lambda_sqs_graph(
        name=name, cloudwatch_data_source=cloudwatch_data_source, fifo=fifo
    )
    dead_letter_sqs_graph = create_lambda_sqs_dlq_graph(
        name=name + "-dlq",
        cloudwatch_data_source=cloudwatch_data_source,
        fifo=fifo,
        notifications=notifications,
    )

    sns_topic_panels = [
        create_sns_graph(
            name=topic,
            cloudwatch_data_source=cloudwatch_data_source,
            notifications=notifications,
        )
        for topic in topics
    ]

    return Dashboard(
        title="{}{}".format(LAMBDA_DASHBOARD_PREFIX, name),
        editable=EDITABLE,
        annotations=get_release_annotations(influxdb_data_source),
        templating=get_release_templating(influxdb_data_source),
        tags=tags,
        timezone=TIMEZONE,
        sharedCrosshair=SHARED_CROSSHAIR,
        rows=[
            Row(title="SNS topics", showTitle=True, collapse=True, panels=sns_topic_panels),
            Row(title="Invocations", showTitle=True, collapse=True,
                panels=[
                    lambda_generate_invocations_graph(name, cloudwatch_data_source, notifications=[]),
                    lambda_generate_duration_graph(name, cloudwatch_data_source),
                ]
            ),
            Row(title="Memory Utilization", showTitle=True, collapse=True,
                panels=[
                    lambda_generate_memory_utilization_percentage_graph(name, cloudwatch_data_source, lambda_insights_namespace, notifications=notifications),
                    lambda_generate_memory_utilization_graph(name, cloudwatch_data_source, lambda_insights_namespace),
                ]
            ),
            Row(title="Logs", showTitle=True, collapse=True,
                panels=[
                    lambda_generate_logs_panel(name, cloudwatch_data_source),
                ]
            ),
            Row(title="Queues", showTitle=True, collapse=True,
                panels=[sqs_graph, dead_letter_sqs_graph]),
        ],
    ).auto_panel_ids()
