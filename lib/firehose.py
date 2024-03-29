"""
    https://docs.aws.amazon.com/firehose/latest/dev/monitoring-with-cloudwatch-metrics.html
"""

from grafanalib.core import SHORT_FORMAT, Dashboard, Graph, Row, Template, single_y_axis
from grafanalib.influxdb import InfluxDBTarget

from lib import colors
from lib.commons import (
    EDITABLE,
    RAW_QUERY,
    RETENTION_POLICY,
    SHARED_CROSSHAIR,
    TIMEZONE,
    TRANSPARENT,
)

FIREHOSE_MEASUREMENT = "cloudwatch_aws_firehose"
FIREHOSE_INCOMING_RECORDS_ALIAS = "Incoming records"
FIREHOSE_DELIVERY_TO_S3_ALIAS = "Delivery to S3"
FIREHOSE_DELIVERY_TO_S3_SUCCESS_ALIAS = "Delivery to S3 Success"


def get_firehose_template(data_source: str) -> Template:
    """Get template for firehose"""

    return Template(
        name="firehose",
        query='SHOW TAG VALUES WITH KEY = "delivery_stream_name" WHERE $timeFilter',
        dataSource=data_source,
        label="Firehose",
        refresh=2,
        allValue="",
        sort=5,
        multi=True,
        includeAll=True,
        hide=0,
    )


def generate_firehose_graph(influxdb_data_source: str) -> Graph:
    """
    Generate Firehose graph
    """

    y_axes = single_y_axis(format=SHORT_FORMAT)

    targets = [
        InfluxDBTarget(
            alias=FIREHOSE_INCOMING_RECORDS_ALIAS,
            query='SELECT sum("incoming_records_sum") FROM "{}"."{}" WHERE ("delivery_stream_name" =~ /^$firehose$/) AND $timeFilter GROUP BY time(5m), "delivery_stream_name" fill(0)'.format(  # noqa: E501
                RETENTION_POLICY, FIREHOSE_MEASUREMENT
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias=FIREHOSE_DELIVERY_TO_S3_SUCCESS_ALIAS,
            query='SELECT sum("delivery_to_s3._success_sum") FROM "{}"."{}" WHERE ("delivery_stream_name" =~ /^$firehose$/) AND $timeFilter GROUP BY time(5m), "delivery_stream_name" fill(0)'.format(  # noqa: E501
                RETENTION_POLICY, FIREHOSE_MEASUREMENT
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias=FIREHOSE_DELIVERY_TO_S3_ALIAS,
            query='SELECT sum("delivery_to_s3._records_sum") FROM "{}"."{}" WHERE ("delivery_stream_name" =~ /^$firehose$/) AND $timeFilter GROUP BY time(5m), "delivery_stream_name" fill(0)'.format(  # noqa: E501
                RETENTION_POLICY, FIREHOSE_MEASUREMENT
            ),
            rawQuery=RAW_QUERY,
        ),
    ]

    series_overrides = [
        {
            "alias": FIREHOSE_INCOMING_RECORDS_ALIAS,
            "color": colors.ORANGE,
        },
        {
            "alias": FIREHOSE_DELIVERY_TO_S3_ALIAS,
            "color": colors.YELLOW,
        },
        {
            "alias": FIREHOSE_DELIVERY_TO_S3_SUCCESS_ALIAS,
            "color": colors.GREEN,
            "zindex": 1,
        },
    ]

    return Graph(
        title="Firehose: $firehose",
        dataSource=influxdb_data_source,
        targets=targets,
        yAxes=y_axes,
        seriesOverrides=series_overrides,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=True,
        lines=False,
    ).auto_ref_ids()


def generate_firehose_dashboard(
    influxdb_data_source: str, environment: str, *args, **kwargs
) -> Dashboard:
    """Generate Firehose dashboard"""
    tags = ["firehose", environment]

    rows = [
        Row(
            panels=[generate_firehose_graph(influxdb_data_source=influxdb_data_source)],
            editable=EDITABLE,
            repeat="firehose",
            title="$firehose",
        )
    ]

    return Dashboard(
        title="Firehose",
        editable=EDITABLE,
        tags=tags,
        timezone=TIMEZONE,
        sharedCrosshair=SHARED_CROSSHAIR,
        rows=rows,
    ).auto_panel_ids()
