#!/usr/bin/env python3

from lib import DashboardEncoder
from lib.lambdas import dispatcher as lambda_dispatcher
from lib.api_gateways import generate_api_gateways_dashboard as apig_dispatcher
import argparse
import json


def parse_options():  # pragma: no cover
    """
    parse cli
    """
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--name", type=str, required=True, help="Name")
    parser.add_argument(
        "--environment", type=str, required=True, help="Environment name"
    )
    parser.add_argument(
        "--data_source", type=str, required=True, help="Datasource name"
    )
    parser.add_argument("--notifications", nargs="+", help="Notify alerts")

    subparsers = parser.add_subparsers(dest="service")
    subparsers.required = True

    apig = subparsers.add_parser(
        "api-gateway", help="Create dashboard for API gateways"
    )
    apig.add_argument("--lambdas", nargs="+", help="List of Lambda names or arns", default=[])

    lambda_function = subparsers.add_parser(
        "lambda", help="Create dashboard for lambdas"
    )
    lambda_function_sub_parser = lambda_function.add_subparsers(dest="trigger")
    lambda_function_sub_parser.required = True

    lambda_function_sub_parser.add_parser(
        "cognito-idp", help="Lambda is triggered by Cognito"
    )
    lambda_function_sub_parser.add_parser(
        "cloudwatch-event-schedule", help="Lambda is triggered by Cron"
    )
    lambda_function_sub_parser.add_parser(
        "cloudwatch-event-trigger", help="Lambda is triggered by Cloudwatch Events"
    )
    lambda_function_sub_parser.add_parser(
        "cloudwatch-logs", help="Lambda is triggered by Cloudwatch logs"
    )
    lambda_function_sub_parser.add_parser(
        "null", help="Lambda is triggered by external forces"
    )

    lambda_sns_triggers = lambda_function_sub_parser.add_parser(
        "sns", help="Lambda is triggered by SNS"
    )
    lambda_sns_triggers.add_argument(
        "--topics", nargs="+", help="List of SNS topics", required=True
    )
    lambda_function_sub_parser.add_parser("sqs", help="Lambda is triggered by SQS")

    return parser.parse_args()


def apply_options(args):
    """Apply options"""
    if args.notifications:
        args.notifications = [
            {"uid": notification} for notification in args.notifications
        ]

    return args


def main():  # pragma: no cover
    """
    main
    """
    args = parse_options()
    args = apply_options(args)
    dispatch = {
        "lambda": lambda_dispatcher,
        "api-gateway": apig_dispatcher
        }
    dashboard = dispatch[args.service](**args.__dict__)
    dashboard_json = json.dumps(dashboard.to_json_data(), cls=DashboardEncoder)
    print(dashboard_json)


if __name__ == "__main__":  # pragma: no cover
    main()
