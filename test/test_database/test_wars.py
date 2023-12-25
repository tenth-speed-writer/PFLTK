import pytest
import datetime

from src import db as data
from src.db import \
    NewerWarAlreadyExistsException, \
    UniqueRowAlreadyExistsException, \
    War
from fixtures import \
    database_fixture, \
    valid_war_fixture
from test_data import VALID_WAR

def test_inserts_valid_war_into_empty_table(database_fixture):
    """Causes no issue when inserting a valid war into an empty table."""
    conn = database_fixture.get_connection()
    data.wars.insert_war(*VALID_WAR, conn)
    conn.commit()

    new_war = War(*data.wars.select_latest_war(conn))
    assert new_war == VALID_WAR

def test_inserts_newer_war_into_occupied_table(valid_war_fixture):
    """
    Causes no issue when inserting a newer valid war into a
    'wars' table which already contains at least one row.
    """
    conn = valid_war_fixture.get_connection()
    newer_war = War(
        war_number=VALID_WAR.war_number + 1,
        pulled_on=VALID_WAR.pulled_on + datetime.timedelta(days=30)
    )
    data.wars.insert_war(*newer_war, conn)
    conn.commit()

    assert War(*data.wars.select_latest_war(conn)) == newer_war

def test_raises_exception_when_given_same_war(valid_war_fixture):
    """
    Raises a UniqueRowAlreadyExistsException when told to insert
    the same war as was inserted by the valid_war_fixture
    """
    conn = valid_war_fixture.get_connection()
    with pytest.raises(UniqueRowAlreadyExistsException):
        data.wars.insert_war(*VALID_WAR, conn)

def test_raises_exception_when_given_older_war(valid_war_fixture):
    """
    Raises a NewerWarAlreadyExistsException when told to insert
    a new war which is older than the most recent one on record
    """
    conn = valid_war_fixture.get_connection()
    older_war = War(
        war_number=VALID_WAR.war_number - 1,
        pulled_on=VALID_WAR.pulled_on - datetime.timedelta(days=30)
    )
    with pytest.raises(NewerWarAlreadyExistsException):
        data.wars.insert_war(*older_war, conn)