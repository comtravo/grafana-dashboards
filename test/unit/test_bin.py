from argparse import Namespace

from bin import apply_options, dispatcher


class TestApplyOptions:
    """Test parse_option"""

    def test_should_generate_notifications_object(self):

        cli_options = Namespace(notifications=["slack-1", "slack-2"])

        expected_notifications_block = [{"uid": "slack-1"}, {"uid": "slack-2"}]

        expected_args = Namespace(notifications=expected_notifications_block)

        apply_options.when.called_with(cli_options).should.return_value(expected_args)

    def test_should_have_all_dispatchers(self):
        handlers = [
            "lambda",
            "api-gateway",
            "step-function",
            "firehose",
            "elasticsearch",
            "elasticsearch-alerts",
            "rds",
        ]

        for handler in handlers:

            dispatcher().should.have.key(handler)
