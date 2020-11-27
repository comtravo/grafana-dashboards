from lib.lambdas import dispatcher

import re


class TestDispatcher:
    def test_should_throw_exception_when_dispatcher_called_with_wrong_arguments(self):
        dispatcher.when.called_with(service="foo", trigger="bar").should.throw(
            Exception, r"dispatcher recieved a non l"
        )

    def test_should_call_trigger_handlers(self):
        expected_triggers = ["cognito", "cron", "events", "logs", "sns", "sqs"]

        for trigger in expected_triggers:
            dispatcher.when.called_with(
                service="lambda", trigger=trigger
            ).should.be.ok
