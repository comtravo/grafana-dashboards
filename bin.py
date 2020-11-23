#!/usr/bin/env python3

import argparse


def parse_options():
    """
    parse cli
    """
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--name", type=str, required=True)
    parser.add_argument("--environment", type=str, required=True)

    subparsers = parser.add_subparsers(dest="service")

    lambda_function = subparsers.add_parser(
        "lambda", help="Create dashboard for lambdas"
    )

    lambda_function_sub_parser = lambda_function.add_subparsers(dest="trigger")
    lambda_function_sub_parser.add_parser("cron", help="Lambda is triggered by Cron")
    lambda_function_sub_parser.add_parser(
        "logs", help="Lambda is triggered by Cloudwatch logs"
    )

    lambda_sns_triggers = lambda_function_sub_parser.add_parser(
        "sns", help="Lambda is triggered by SNS"
    )
    lambda_sns_triggers.add_argument(
        "--topics", type=list, help="List of SNS topics", required=True
    )

    lambda_sns_triggers = lambda_function_sub_parser.add_parser(
        "sqs", help="Lambda is triggered by SQS"
    )

    return parser.parse_args()


def main():
    """
    main
    """
    args = parse_options()
    print(args)


if __name__ == "__main__":
    main()
