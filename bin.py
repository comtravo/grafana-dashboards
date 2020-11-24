#!/usr/bin/env python3

from lib import DashboardEncoder
from lib.lambdas import dispatcher as lambda_dispatcher
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
    parser.add_argument(
        "--data_source", type=str, required=True, help="Datasource name"
    )
    parser.add_argument("--alert", action="store_true", help="Create alert")

    subparsers = parser.add_subparsers(dest="service")
    subparsers.required = True

    lambda_function = subparsers.add_parser(
        "lambda", help="Create dashboard for lambdas"
    )

    lambda_function_sub_parser = lambda_function.add_subparsers(dest="trigger")
    lambda_function_sub_parser.required = True

    lambda_function_sub_parser.add_parser(
        "cognito", help="Lambda is triggered by Cognito"
    )
    lambda_function_sub_parser.add_parser("cron", help="Lambda is triggered by Cron")
    lambda_function_sub_parser.add_parser(
        "events", help="Lambda is triggered by Cloudwatch Events"
    )
    lambda_function_sub_parser.add_parser(
        "logs", help="Lambda is triggered by Cloudwatch logs"
    )

    lambda_sns_triggers = lambda_function_sub_parser.add_parser(
        "sns", help="Lambda is triggered by SNS"
    )
    lambda_sns_triggers.add_argument(
        "--topics", nargs="+", help="List of SNS topics", required=True
    )
    lambda_function_sub_parser.add_parser("sqs", help="Lambda is triggered by SQS")

    return parser.parse_args()


def main():
    """
    main
    """
    args = parse_options()

    dispatch = {"lambda": lambda_dispatcher}
    # print(args)
    # exit(0)
    dashboard = dispatch[args.service](**args.__dict__)
    print(json.dumps(dashboard.to_json_data(), cls=DashboardEncoder))


if __name__ == "__main__":
    main()
