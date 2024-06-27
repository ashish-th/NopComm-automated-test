import os
from datetime import date


# result class to Hold result
class TestResult:
    failed: int
    passed: int
    skipped: int
    error: int
    deselected: int
    xfailed: int
    xpassed: int
    failed_list = []


# slack template

class SlackTemplate:

    def __init__(self, result: TestResult, properties, link, env):
        self.env =env
        self.reports = result
        self.test_properties = properties
        self.link = link
        self.pass_color = self.broken_color = self.fail_color = "#56a64f"
        self.misc_color = "#cbcfc9"
        if self.reports.failed > 0:
            self.fail_color = "#e00404"
        if self.reports.error > 0:
            self.broken_color = "warning"
        self.failed_str = ('\n'.join(['{}) {}'.format(i, val) for i, val in (enumerate(self.reports.failed_list, 1))]))

    @staticmethod
    def __get_current_date():
        """
        Returns:
            Date with following format - DD-MM-YYYY
        """
        today = date.today()
        return f"{today.month}/{today.day}/{today.year}"

    def __slack_header(self):
        return [
            {
                "type": "divider"
            },

            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{self.test_properties['Name']} -Result Summary",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Environment:*\n{self.env}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Execution Date:*\n{self.__get_current_date()}"
                    }]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Report: <{self.link}|link>"
                }
            }

        ]

    def __slack_body(self):
        return [
            {
                "text": f"Passed   Count: *{self.reports.passed + self.reports.xpassed}*",
                "mrkdwn_in": [
                    "text"
                ],
                "color": f"{self.pass_color}"
            },
            {
                "text": f"Broken   Count: *{self.reports.error}*",
                "mrkdwn_in": [
                    "text"
                ],
                "color": f"{self.broken_color}"
            },

            {
                "text": f"Failed     Count: *{self.reports.failed}*",
                "mrkdwn_in": [
                    "text"
                ],
                "color": f"{self.fail_color}"
            },
            {
                "text": f"Skipped  Count: *{self.reports.skipped}*",
                "mrkdwn_in": [
                    "text"
                ],
                "color": f"{self.misc_color}"
            },
            {
                "text": f"Xfailed  Count: *{self.reports.xfailed}*",
                "mrkdwn_in": [
                    "text"
                ],
                "color": f"{self.misc_color}"
            },
            {
                "text": f"XPassed Count: *{self.reports.xpassed}*",
                "mrkdwn_in": [
                    "text"
                ],
                "color": f"{self.pass_color}"
            },

            {
                "type": "divider"
            },
            {
                "title": "Failed Scripts",
                "color": f"{self.fail_color}",
                "text": f"{self.failed_str}",
                "mrkdwn_in": [
                    "text"
                ]
            }
        ]

    def constructed_message_format(self):
        return {

            "blocks": self.__slack_header(),
            "attachments": self.__slack_body()

        }
