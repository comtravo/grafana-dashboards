#!/usr/bin/env python3

from lib import DashboardEncoder
from lib.lambdas import lambda_cron_dashboard
import argparse
import json


def parse_options():
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
    parser.add_argument("--dataSource", type=str, required=True, help="Datasource name")
    parser.add_argument("--alert", type=bool, default=True, help="Create alert")

    subparsers = parser.add_subparsers(dest="service")
    subparsers.required = True

    lambda_function = subparsers.add_parser(
        "lambda", help="Create dashboard for lambdas"
    )

    lambda_function_sub_parser = lambda_function.add_subparsers(dest="trigger")
    lambda_function_sub_parser.required = True
    lambda_function_sub_parser.add_parser("cron", help="Lambda is triggered by Cron")
    lambda_function_sub_parser.add_parser(
        "logs", help="Lambda is triggered by Cloudwatch logs"
    )
    lambda_function_sub_parser.add_parser("sqs", help="Lambda is triggered by SQS")

    lambda_sns_triggers = lambda_function_sub_parser.add_parser(
        "sns", help="Lambda is triggered by SNS"
    )
    lambda_sns_triggers.add_argument(
        "--topics", type=list, help="List of SNS topics", required=True
    )

    return parser.parse_args()


def main():
    """
    main
    """
    args = parse_options()
    # print(args)
    # print(dir(args))
    dashboard = lambda_cron_dashboard(**args.__dict__)
    print(json.dumps(dashboard.to_json_data(), cls=DashboardEncoder))


if __name__ == "__main__":
    main()
