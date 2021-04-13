#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import unittest

import httpretty
import requests

if sys.version_info >= (3, 0):
    from unittest.mock import patch
else:
    from mock import patch

from shellfoundry.exceptions import NoVersionsHaveBeenFoundException
from shellfoundry.utilities.template_versions import VERSIONS_URL, TemplateVersions


def mock_get_branches_from_github():
    return """[
  {
    "name": "5.0.0",
    "commit": {
      "sha": "efe253280a3346c2be23b1a9af4113f2b989f26c",
      "url": "https://api.github.com/repos/user/repo/commits/efe253280a3346c2be23b1a9af4113f2b989f26c"  # noqa: E501
    }
  },
  {
    "name": "5.0.1",
    "commit": {
      "sha": "e67ec4de2f00fabfe7be35fe412ec400847ccc7d",
      "url": "https://api.github.com/repos/user/repo/commits/e67ec4de2f00fabfe7be35fe412ec400847ccc7d"
    }
  },
  {
    "name": "5.0.2",
    "commit": {
      "sha": "421c20b231b11672411f39f813c93d0f82723f3a",
      "url": "https://api.github.com/repos/user/repo/commits/421c20b231b11672411f39f813c93d0f82723f3a"
    }
  },
  {
    "name": "master",
    "commit": {
      "sha": "b8687aef6a15a4fd9c6daa6b7549470e9e3c4c11",
      "url": "https://api.github.com/repos/user/repo/commits/b8687aef6a15a4fd9c6daa6b7549470e9e3c4c11"
    }
  }
]
"""


class TestTemplateVersions(unittest.TestCase):
    @httpretty.activate
    def test_get_versions_of_template_error_due_to_request_failed(self):
        # Arrange
        user, repo = "user", "repo"
        httpretty.register_uri(
            "GET", VERSIONS_URL.format(*(user, repo)), status=requests.codes.bad
        )

        # Act
        with self.assertRaises(requests.HTTPError) as context:
            TemplateVersions(user, repo).get_versions_of_template()

        # Assert
        self.assertEqual(
            context.exception.message, "Failed to receive versions from host"
        )

    @httpretty.activate
    def test_get_versions_of_template_and_has_no_versions_failure(self):
        # Arrange
        user, repo = "user", "repo"
        httpretty.register_uri(
            "GET",
            VERSIONS_URL.format(*(user, repo)),
            body=mock_get_branches_from_github(),
        )

        # Act
        with patch(
            "shellfoundry.utilities.template_versions.TemplateVersions.has_versions",
            return_value=False,
        ):
            with self.assertRaises(NoVersionsHaveBeenFoundException) as context:
                TemplateVersions(user, repo).get_versions_of_template()

        # Assert
        self.assertEqual(
            context.exception.message, "No versions have been found for this template"
        )

    @httpretty.activate
    def test_get_versions_of_template_reversed_success(self):
        # Arrange
        user, repo = "user", "repo"
        httpretty.register_uri(
            "GET",
            VERSIONS_URL.format(*(user, repo)),
            body=mock_get_branches_from_github(),
        )

        # Act
        versions = TemplateVersions(user, repo).get_versions_of_template()

        # Assert
        self.assertSequenceEqual(versions, ["5.0.2", "5.0.1", "5.0.0", "master"])
