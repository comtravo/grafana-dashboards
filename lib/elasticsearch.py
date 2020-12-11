"""
    https://docs.aws.amazon.com/elasticsearch-service/latest/developerguide/es-managedomains-cloudwatchmetrics.html
"""

from grafanalib.core import (
    Dashboard,
    Graph,
    PERCENT_FORMAT,
    Repeat,
    Row,
    SHORT_FORMAT,
    Template,
    Templating,
    single_y_axis,
    YAxes,
    YAxis,
)
from grafanalib.formatunits import MEGA_BYTES
from grafanalib.influxdb import InfluxDBTarget

from lib.annotations import get_release_annotations
from lib.templating import get_release_template
from lib import colors
from lib.commons import (
    EDITABLE,
    RAW_QUERY,
    RETENTION_POLICY,
    SHARED_CROSSHAIR,
    TIMEZONE,
    TRANSPARENT,
)

ES_MEASUREMENT = "cloudwatch_aws_es"


def get_elasticsearch_template(data_source: str):
    """Get template for elasticsearch"""

    return Template(
        name="elasticsearch",
        query='SHOW TAG VALUES WITH KEY = "domain_name" WHERE $timeFilter',
        dataSource=data_source,
        label="Elasticsearch",
        refresh=2,
        allValue="",
        sort=5,
        multi=False,
        includeAll=False,
        hide=0,
    )


def generate_elasticsearch_cpu_graph(data_source: str):
    """
    Generate Elasticsearch graph
    """

    y_axes = single_y_axis(format=PERCENT_FORMAT)
    alias = "CPU utilization"

    targets = [
        InfluxDBTarget(
            alias=alias,
            query='SELECT max("cpu_utilization_maximum") FROM "{}"."{}" WHERE ("domain_name" =~ /^$elasticsearch$/) AND $timeFilter GROUP BY time(1m) fill(previous)'.format(
                RETENTION_POLICY, ES_MEASUREMENT
            ),
            rawQuery=RAW_QUERY,
        )
    ]

    series_overrides = [
        {
            "alias": alias,
            "color": colors.GREEN,
            "lines": True,
            "bars": False,
        }
    ]

    return Graph(
        title=alias,
        dataSource=data_source,
        targets=targets,
        yAxes=y_axes,
        seriesOverrides=series_overrides,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=True,
        lines=False,
    ).auto_ref_ids()


def generate_elasticsearch_jvm_memory_pressure_graph(data_source: str):
    """
    Generate Elasticsearch graph
    """

    y_axes = single_y_axis(format=PERCENT_FORMAT)
    alias = "JVM memory pressure"

    targets = [
        InfluxDBTarget(
            alias=alias,
            query='SELECT max("jvm_memory_pressure_maximum") FROM "{}"."{}" WHERE ("domain_name" =~ /^$elasticsearch$/) AND $timeFilter GROUP BY time(1m) fill(previous)'.format(
                RETENTION_POLICY, ES_MEASUREMENT
            ),
            rawQuery=RAW_QUERY,
        )
    ]

    series_overrides = [
        {
            "alias": alias,
            "color": colors.GREEN,
            "lines": True,
            "bars": False,
        }
    ]

    return Graph(
        title=alias,
        dataSource=data_source,
        targets=targets,
        yAxes=y_axes,
        seriesOverrides=series_overrides,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=True,
        lines=False,
    ).auto_ref_ids()


def generate_elasticsearch_documents_graph(data_source: str):
    """
    Generate Elasticsearch graph
    """

    y_axes = YAxes(
        YAxis(format=SHORT_FORMAT),
        YAxis(format=SHORT_FORMAT),
    )
    searchable_documents_alias = "Searchable documents"
    deleted_documents_alias = "Deleted documents"

    targets = [
        InfluxDBTarget(
            alias=searchable_documents_alias,
            query='SELECT max("searchable_documents_maximum") FROM "{}"."{}" WHERE ("domain_name" =~ /^$elasticsearch$/) AND $timeFilter GROUP BY time(1m) fill(previous)'.format(
                RETENTION_POLICY, ES_MEASUREMENT
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias=deleted_documents_alias,
            query='SELECT max("deleted_documents_maximum") FROM "{}"."{}" WHERE ("domain_name" =~ /^$elasticsearch$/) AND $timeFilter GROUP BY time(1m) fill(previous)'.format(
                RETENTION_POLICY, ES_MEASUREMENT
            ),
            rawQuery=RAW_QUERY,
        ),
    ]

    series_overrides = [
        {
            "alias": searchable_documents_alias,
            "color": colors.GREEN,
            "lines": True,
            "bars": False,
        },
        {
            "alias": deleted_documents_alias,
            "color": colors.ORANGE,
            "lines": True,
            "bars": False,
            "yaxis": 2,
        },
    ]

    return Graph(
        title="Documents",
        dataSource=data_source,
        targets=targets,
        yAxes=y_axes,
        seriesOverrides=series_overrides,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=True,
        lines=False,
    ).auto_ref_ids()


def generate_elasticsearch_storage_graph(data_source: str):
    """
    Generate Elasticsearch graph
    """

    y_axes = YAxes(
        YAxis(format=MEGA_BYTES),
        YAxis(format=MEGA_BYTES),
    )
    free_storage_alias = "Free storage"
    cluster_used_space_alias = "Used space"

    targets = [
        InfluxDBTarget(
            alias=free_storage_alias,
            query='SELECT min("free_storage_space_minimum") FROM "{}"."{}" WHERE ("domain_name" =~ /^$elasticsearch$/) AND $timeFilter GROUP BY time(1m) fill(previous)'.format(
                RETENTION_POLICY, ES_MEASUREMENT
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias=cluster_used_space_alias,
            query='SELECT max("cluster_used_space_maximum") FROM "{}"."{}" WHERE ("domain_name" =~ /^$elasticsearch$/) AND $timeFilter GROUP BY time(1m) fill(previous)'.format(
                RETENTION_POLICY, ES_MEASUREMENT
            ),
            rawQuery=RAW_QUERY,
        ),
    ]

    series_overrides = [
        {
            "alias": free_storage_alias,
            "color": colors.GREEN,
            "lines": True,
            "bars": False,
        },
        {
            "alias": cluster_used_space_alias,
            "color": colors.ORANGE,
            "lines": True,
            "bars": False,
            "yaxis": 2,
        },
    ]

    return Graph(
        title="Storage",
        dataSource=data_source,
        targets=targets,
        yAxes=y_axes,
        seriesOverrides=series_overrides,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=True,
        lines=False,
    ).auto_ref_ids()

def generate_elasticsearch_requests_graph(data_source: str):
    """
    Generate Elasticsearch graph
    """

    y_axes = YAxes(
        YAxis(format=SHORT_FORMAT),
        YAxis(format=SHORT_FORMAT),
    )
    xx2_alias = "2xx"
    xx3_alias = "3xx"
    xx4_alias = "4xx"
    xx5_alias = "5xx"

    cluster_used_space_alias = "Used space"

    targets = [
        InfluxDBTarget(
            alias=xx2_alias,
            query='SELECT max("2xx_sum") FROM "{}"."{}" WHERE ("domain_name" =~ /^$elasticsearch$/) AND $timeFilter GROUP BY time(1m) fill(0)'.format(
                RETENTION_POLICY, ES_MEASUREMENT
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias=xx3_alias,
            query='SELECT max("3xx_sum") FROM "{}"."{}" WHERE ("domain_name" =~ /^$elasticsearch$/) AND $timeFilter GROUP BY time(1m) fill(0)'.format(
                RETENTION_POLICY, ES_MEASUREMENT
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias=xx4_alias,
            query='SELECT max("4xx_sum") FROM "{}"."{}" WHERE ("domain_name" =~ /^$elasticsearch$/) AND $timeFilter GROUP BY time(1m) fill(0)'.format(
                RETENTION_POLICY, ES_MEASUREMENT
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias=xx5_alias,
            query='SELECT max("5xx_sum") FROM "{}"."{}" WHERE ("domain_name" =~ /^$elasticsearch$/) AND $timeFilter GROUP BY time(1m) fill(0)'.format(
                RETENTION_POLICY, ES_MEASUREMENT
            ),
            rawQuery=RAW_QUERY,
        ),
    ]

    series_overrides = [
        {
            "alias": xx2_alias,
            "color": colors.GREEN,
            "lines": True,
            "bars": False,
        },
        {
            "alias": xx3_alias,
            "color": colors.YELLOW,
            "lines": True,
            "bars": False,
        },
        {
            "alias": xx4_alias,
            "color": colors.ORANGE,
            "lines": True,
            "bars": False,
        },
        {
            "alias": xx5_alias,
            "color": colors.ORANGE,
            "lines": True,
            "bars": False,
        },
    ]

    return Graph(
        title="Requests",
        dataSource=data_source,
        targets=targets,
        yAxes=y_axes,
        seriesOverrides=series_overrides,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=True,
        lines=False,
    ).auto_ref_ids()


def generate_elasticsearch_dashboard(
    data_source: str, environment: str, *args, **kwargs
):
    """Generate Elasticsearch dashboard"""
    tags = ["elasticsearch", environment]

    templating = Templating(
        [
            get_elasticsearch_template(data_source=data_source),
            get_release_template(data_source=data_source),
        ]
    )

    rows = [
        Row(
            panels=[
                generate_elasticsearch_cpu_graph(data_source=data_source),
                generate_elasticsearch_jvm_memory_pressure_graph(
                    data_source=data_source
                ),
            ],
            editable=EDITABLE,
        ),
        Row(
            panels=[generate_elasticsearch_documents_graph(data_source=data_source)],
            editable=EDITABLE,
        ),
        Row(
            panels=[generate_elasticsearch_storage_graph(data_source=data_source)],
            editable=EDITABLE,
        ),
        Row(
            panels=[generate_elasticsearch_requests_graph(data_source=data_source)],
            editable=EDITABLE,
        ),
    ]

    return Dashboard(
        title="Elasticsearch",
        editable=EDITABLE,
        annotations=get_release_annotations(data_source=data_source),
        templating=templating,
        tags=tags,
        timezone=TIMEZONE,
        sharedCrosshair=SHARED_CROSSHAIR,
        rows=rows,
    ).auto_panel_ids()
