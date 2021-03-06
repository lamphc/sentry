from __future__ import absolute_import

from sentry.api.event_search import (
    InvalidSearchQuery,
    SearchFilter,
    SearchKey,
    SearchValue,
)
from sentry.api.issue_search import (
    convert_actor_value,
    convert_query_values,
    convert_user_value,
    parse_search_query,
    value_converters,
)
from sentry.constants import STATUS_CHOICES
from sentry.testutils import TestCase


class ParseSearchQueryTest(TestCase):
    def test_key_mappings(self):
        # Test a couple of keys to ensure things are working as expected
        assert parse_search_query('bookmarks:123') == [
            SearchFilter(
                key=SearchKey(name='bookmarked_by'),
                operator='=',
                value=SearchValue('123'),
            )
        ]
        assert parse_search_query('first-release:123') == [
            SearchFilter(
                key=SearchKey(name='first_release'),
                operator='=',
                value=SearchValue('123'),
            )
        ]
        assert parse_search_query('first-release:123 non_mapped:456') == [
            SearchFilter(
                key=SearchKey(name='first_release'),
                operator='=',
                value=SearchValue('123'),
            ),
            SearchFilter(
                key=SearchKey(name='non_mapped'),
                operator='=',
                value=SearchValue('456'),
            ),
        ]

    def test_is_query_unassigned(self):
        assert parse_search_query('is:unassigned') == [
            SearchFilter(
                key=SearchKey(name='unassigned'),
                operator='=',
                value=SearchValue(True),
            ),
        ]
        assert parse_search_query('is:assigned') == [
            SearchFilter(
                key=SearchKey(name='unassigned'),
                operator='=',
                value=SearchValue(False),
            ),
        ]

        assert parse_search_query('!is:unassigned') == [
            SearchFilter(
                key=SearchKey(name='unassigned'),
                operator='!=',
                value=SearchValue(True),
            ),
        ]
        assert parse_search_query('!is:assigned') == [
            SearchFilter(
                key=SearchKey(name='unassigned'),
                operator='!=',
                value=SearchValue(False),
            ),
        ]

    def test_is_query_status(self):
        for status_string, status_val in STATUS_CHOICES.items():
            assert parse_search_query('is:%s' % status_string) == [
                SearchFilter(
                    key=SearchKey(name='status'),
                    operator='=',
                    value=SearchValue(status_val),
                ),
            ]
            assert parse_search_query('!is:%s' % status_string) == [
                SearchFilter(
                    key=SearchKey(name='status'),
                    operator='!=',
                    value=SearchValue(status_val),
                ),
            ]

    def test_is_query_invalid(self):
        with self.assertRaises(InvalidSearchQuery) as cm:
            parse_search_query('is:wrong')

        assert cm.exception.message.startswith(
            'Invalid value for "is" search, valid values are',
        )


class ConvertQueryValuesTest(TestCase):

    def test_valid_converter(self):
        filters = [SearchFilter(SearchKey('assigned_to'), '=', SearchValue('me'))]
        expected = value_converters['assigned_to'](
            filters[0].value.raw_value,
            [self.project],
            self.user,
        )
        filters = convert_query_values(filters, [self.project], self.user)
        assert filters[0].value.raw_value == expected

    def test_no_converter(self):
        search_val = SearchValue('me')
        filters = [SearchFilter(SearchKey('something'), '=', search_val)]
        filters = convert_query_values(filters, [self.project], self.user)
        assert filters[0].value.raw_value == search_val.raw_value


class ConvertActorValueTest(TestCase):
    def test_user(self):
        assert convert_actor_value(
            'me',
            [self.project],
            self.user,
        ) == convert_user_value('me', [self.project], self.user)

    def test_team(self):
        assert convert_actor_value(
            '#%s' % self.team.slug,
            [self.project],
            self.user,
        ) == self.team

    def test_invalid_team(self):
        assert convert_actor_value(
            '#never_upgrade',
            [self.project],
            self.user,
        ).id == 0


class ConvertUserValueTest(TestCase):
    def test_me(self):
        assert convert_user_value('me', [self.project], self.user) == self.user

    def test_specified_user(self):
        user = self.create_user()
        assert convert_user_value(user.username, [self.project], self.user) == user

    def test_invalid_user(self):
        assert convert_user_value('fake-user', [], None).id == 0
