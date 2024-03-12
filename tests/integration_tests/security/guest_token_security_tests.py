# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""Unit tests for Superset"""
import json
from unittest import mock

import pytest
from flask import g

from superset import db, security_manager
from superset.connectors.sqla.models import SqlaTable
from superset.daos.dashboard import EmbeddedDashboardDAO
from superset.dashboards.commands.exceptions import DashboardAccessDeniedError
from superset.exceptions import SupersetSecurityException
from superset.models.dashboard import Dashboard
from superset.security.guest_token import GuestTokenResourceType
from superset.sql_parse import Table
from superset.utils.database import get_example_database
from tests.integration_tests.base_tests import SupersetTestCase
from tests.integration_tests.fixtures.birth_names_dashboard import (
    load_birth_names_dashboard_with_slices,
    load_birth_names_data,
)


@mock.patch.dict(
    "superset.extensions.feature_flag_manager._feature_flags",
    EMBEDDED_SUPERSET=True,
)
class TestGuestUserSecurity(SupersetTestCase):
    def authorized_guest(self):
        return security_manager.get_guest_user_from_token(
            {"user": {}, "resources": [{"type": "dashboard", "id": "some-uuid"}]}
        )

    def test_is_guest_user__regular_user(self):
        is_guest = security_manager.is_guest_user(security_manager.find_user("admin"))
        self.assertFalse(is_guest)

    def test_is_guest_user__anonymous(self):
        is_guest = security_manager.is_guest_user(security_manager.get_anonymous_user())
        self.assertFalse(is_guest)

    def test_is_guest_user__guest_user(self):
        is_guest = security_manager.is_guest_user(self.authorized_guest())
        self.assertTrue(is_guest)

    @mock.patch.dict(
        "superset.extensions.feature_flag_manager._feature_flags",
        EMBEDDED_SUPERSET=False,
    )
    def test_is_guest_user__flag_off(self):
        is_guest = security_manager.is_guest_user(self.authorized_guest())
        self.assertFalse(is_guest)

    def test_get_guest_user__regular_user(self):
        g.user = security_manager.find_user("admin")
        guest_user = security_manager.get_current_guest_user_if_guest()
        self.assertIsNone(guest_user)

    def test_get_guest_user__anonymous_user(self):
        g.user = security_manager.get_anonymous_user()
        guest_user = security_manager.get_current_guest_user_if_guest()
        self.assertIsNone(guest_user)

    def test_get_guest_user__guest_user(self):
        g.user = self.authorized_guest()
        guest_user = security_manager.get_current_guest_user_if_guest()
        self.assertEqual(guest_user, g.user)

    def test_get_guest_user_roles_explicit(self):
        guest = self.authorized_guest()
        roles = security_manager.get_user_roles(guest)
        self.assertEqual(guest.roles, roles)

    def test_get_guest_user_roles_implicit(self):
        guest = self.authorized_guest()
        g.user = guest

        roles = security_manager.get_user_roles()
        self.assertEqual(guest.roles, roles)


@mock.patch.dict(
    "superset.extensions.feature_flag_manager._feature_flags",
    EMBEDDED_SUPERSET=True,
)
@pytest.mark.usefixtures("load_birth_names_dashboard_with_slices")
class TestGuestUserDashboardAccess(SupersetTestCase):
    def setUp(self) -> None:
        self.dash = db.session.query(Dashboard).filter_by(slug="births").first()
        self.embedded = EmbeddedDashboardDAO.upsert(self.dash, [])
        self.authorized_guest = security_manager.get_guest_user_from_token(
            {
                "user": {},
                "resources": [{"type": "dashboard", "id": str(self.embedded.uuid)}],
            }
        )
        self.unauthorized_guest = security_manager.get_guest_user_from_token(
            {
                "user": {},
                "resources": [
                    {"type": "dashboard", "id": "06383667-3e02-4e5e-843f-44e9c5896b6c"}
                ],
            }
        )

    def test_has_guest_access__regular_user(self):
        g.user = security_manager.find_user("admin")
        has_guest_access = security_manager.has_guest_access(self.dash)
        self.assertFalse(has_guest_access)

    def test_has_guest_access__anonymous_user(self):
        g.user = security_manager.get_anonymous_user()
        has_guest_access = security_manager.has_guest_access(self.dash)
        self.assertFalse(has_guest_access)

    def test_has_guest_access__authorized_guest_user(self):
        g.user = self.authorized_guest
        has_guest_access = security_manager.has_guest_access(self.dash)
        self.assertTrue(has_guest_access)

    def test_has_guest_access__authorized_guest_user__non_zero_resource_index(self):
        # set up a user who has authorized access, plus another resource
        guest = self.authorized_guest
        guest.resources = [
            {"type": "dashboard", "id": "not-a-real-id"}
        ] + guest.resources
        g.user = guest

        has_guest_access = security_manager.has_guest_access(self.dash)
        self.assertTrue(has_guest_access)

    def test_has_guest_access__unauthorized_guest_user__different_resource_id(self):
        g.user = security_manager.get_guest_user_from_token(
            {
                "user": {},
                "resources": [{"type": "dashboard", "id": "not-a-real-id"}],
            }
        )
        has_guest_access = security_manager.has_guest_access(self.dash)
        self.assertFalse(has_guest_access)

    def test_has_guest_access__unauthorized_guest_user__different_resource_type(self):
        g.user = security_manager.get_guest_user_from_token(
            {"user": {}, "resources": [{"type": "dirt", "id": self.embedded.uuid}]}
        )
        has_guest_access = security_manager.has_guest_access(self.dash)
        self.assertFalse(has_guest_access)

    def test_chart_raise_for_access_as_guest(self):
        chart = self.dash.slices[0]
        g.user = self.authorized_guest

        security_manager.raise_for_access(viz=chart)

    def test_chart_raise_for_access_as_unauthorized_guest(self):
        chart = self.dash.slices[0]
        g.user = self.unauthorized_guest

        with self.assertRaises(SupersetSecurityException):
            security_manager.raise_for_access(viz=chart)

    def test_dataset_raise_for_access_as_guest(self):
        dataset = self.dash.slices[0].datasource
        g.user = self.authorized_guest

        security_manager.raise_for_access(datasource=dataset)

    def test_dataset_raise_for_access_as_unauthorized_guest(self):
        dataset = self.dash.slices[0].datasource
        g.user = self.unauthorized_guest

        with self.assertRaises(SupersetSecurityException):
            security_manager.raise_for_access(datasource=dataset)

    def test_guest_token_does_not_grant_access_to_underlying_table(self):
        sqla_table = self.dash.slices[0].table
        table = Table(table=sqla_table.table_name)

        g.user = self.authorized_guest

        with self.assertRaises(Exception):
            security_manager.raise_for_access(table=table, database=sqla_table.database)

    def test_raise_for_dashboard_access_as_guest(self):
        g.user = self.authorized_guest

        security_manager.raise_for_dashboard_access(self.dash)

    def test_raise_for_dashboard_access_as_unauthorized_guest(self):
        g.user = self.unauthorized_guest

        with self.assertRaises(DashboardAccessDeniedError):
            security_manager.raise_for_dashboard_access(self.dash)

    def test_raise_for_dashboard_access_as_guest_no_rbac(self):
        """
        Test that guest account has no access to other dashboards.

        A bug in the ``raise_for_dashboard_access`` logic allowed the guest user to
        fetch data from other dashboards, as long as the other dashboard:

          - was not embedded AND
            - was not published OR
            - had at least 1 datasource that the user had access to.

        """
        g.user = self.unauthorized_guest

        # Create a draft dashboard that is not embedded
        dash = Dashboard()
        dash.dashboard_title = "My Dashboard"
        dash.owners = []
        dash.slices = []
        dash.published = False
        db.session.add(dash)
        db.session.commit()

        with self.assertRaises(DashboardAccessDeniedError):
            security_manager.raise_for_dashboard_access(dash)

        db.session.delete(dash)
        db.session.commit()

    def test_can_access_datasource_used_in_dashboard_filter(self):
        """
        Test that a user can access a datasource used only by a filter in a dashboard
        they have access to.
        """
        # Create a test dataset
        test_dataset = SqlaTable(
            database_id=get_example_database().id,
            schema="main",
            table_name="test_table_embedded_filter",
        )
        db.session.add(test_dataset)
        db.session.commit()

        # Create an embedabble dashboard with a filter powered by the test dataset
        test_dashboard = Dashboard()
        test_dashboard.dashboard_title = "Test Embedded Dashboard"
        test_dashboard.json_metadata = json.dumps(
            {
                "native_filter_configuration": [
                    {"targets": [{"datasetId": test_dataset.id}]}
                ]
            }
        )
        test_dashboard.owners = []
        test_dashboard.slices = []
        test_dashboard.published = False
        db.session.add(test_dashboard)
        db.session.commit()
        self.embedded = EmbeddedDashboardDAO.upsert(test_dashboard, [])

        # grant access to the dashboad
        g.user = self.authorized_guest
        g.user.resources = [{"type": "dashboard", "id": str(self.embedded.uuid)}]
        g.user.roles = [security_manager.get_public_role()]

        # The user should have access to the datasource via the dashboard
        security_manager.raise_for_access(datasource=test_dataset)

        db.session.delete(test_dashboard)
        db.session.delete(test_dataset)
        db.session.commit()