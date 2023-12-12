import pytest
import datetime
from typing import List
from ...src import db as data
from ...src.db import \
    War, \
    Map, \
    Label, \
    Ticket
from .fixtures import \
    database_fixture, \
    valid_war_fixture, \
    valid_maps_fixture, \
    valid_labels_fixture, \
    VALID_WAR, \
    VALID_MAPS, \
    VALID_LABELS

VALID_TICKETS: List[Ticket] = [
    Ticket(
        war_number=VALID_WAR.war_number,
        destination_map_name=VALID_MAPS[0].map_name,
        destination_x=[
            label for label in VALID_LABELS
            if label.map_name == VALID_MAPS[0].map_name
        ][0].x,
        destination_y=[
            label for label in VALID_LABELS
            if label.map_name == VALID_MAPS[0].map_name
        ][0].y,
        destination_description="The bunker base near the thing",
        origin_map_name=None,
        origin_x=None,
        origin_y=None,
        origin_description=None,
        objective_description="Bring some bmats for building",
        created_on = datetime.datetime.now() - datetime.timedelta(hours=4)
    ),
    Ticket(
        war_number=VALID_WAR.war_number,
        destination_map_name = VALID_MAPS[0].map_name,
        destination_x=[
            label for label in VALID_LABELS
            if label.map_name == VALID_MAPS[0].map_name
        ][0].x,
        destination_y=[
            label for label in VALID_LABELS
            if label.map_name == VALID_MAPS[0].map_name
        ][0].y,
        destination_description="Supply Depot by the lake",
        origin_map_name=VALID_MAPS[1].map_name,
        origin_x=[
            label for label in VALID_LABELS
            if label.map_name == VALID_MAPS[1].map_name
        ][0].x,
        origin_y=[
            label for label in VALID_LABELS
            if label.map_name == VALID_MAPS[1].map_name
        ][0].y,
        origin_description="The facility at the intersection",
        objective_description="Schlep facility tripod weapons to a forward supply depot",
        created_on=datetime.datetime.now() - datetime.timedelta(hours=1)
    )
]

class TestInsertTicket:
    def test_insert_valid_ticket_with_origin(self, valid_maps_fixture):
        """Assures it inserts a ticket with origin data"""
        # Get connection from fixture
        conn = valid_maps_fixture.get_connection()

        # Create a valid imaginary ticket with a specified origin
        ticket = VALID_TICKETS[1]
        ticket_id = data.tickets.insert_ticket(ticket, conn)

        # Assert the ticket ID returns data
        assert data.tickets.select_ticket(ticket_id, conn) == ticket

    def test_insert_valid_ticket_without_origin(self, valid_maps_fixture):
        """Assures it inserts a ticket without origin data"""
        # Get connection from fixture
        conn = valid_maps_fixture.get_connection()

        # Create a valid imaginary ticket without an origin
        ticket = VALID_TICKETS[0]
        ticket_id = data.tickets.insert_ticket(ticket, conn)

        # Assert the ticket ID returns data
        assert data.tickets.select_ticket(ticket_id, conn) == ticket

    def test_insert_valid_ticket_with_partial_origin(
        self,
        valid_maps_fixture
    ):
        """
        Assures it skips inserting the origin if part of it is not supplied.
        """
        # Get a database connection
        conn = valid_maps_fixture.get_connection()

        # Fudge together a ticket with only partial origin data
        valid_ticket = VALID_TICKETS[1]
        ticket = Ticket(
            war_number=valid_ticket.war_number,
            destination_map_name=valid_ticket.destination_map_name,
            destination_x=valid_ticket.destination_x,
            destination_y=valid_ticket.destination_y,
            destination_description=valid_ticket.destination_description,
            origin_map_name=valid_ticket.origin_map_name,
            origin_x=valid_ticket.origin_x,
            origin_y=None,
            origin_description=None,
            objective_description=valid_ticket.objective_description,
            created_on=valid_ticket.created_on
        )

        # Ensure it inserts without issue
        ticket_id = data.tickets.insert_ticket(ticket, conn)

        assert \
            data.tickets.select_ticket(ticket_id, conn).destination_description \
            == ticket.destination_description

    def test_raises_exception_for_old_war(self, valid_labels_fixture):
        """Assures it raises an exception when given an old war."""
        conn = valid_labels_fixture.get_connection()

        ticket_with_bad_war = Ticket(
            VALID_WAR.war_number - 1,
            *VALID_TICKETS[1][1:]
        )

        with pytest.raises(data.CannotCreateTicketForWarException):
            ticket_id = data.tickets.insert_ticket(
                ticket_with_bad_war,
                conn
            )
    
    def test_raises_exception_for_war_that_does_not_exist_yet(
        self,
        valid_labels_fixture
    ):
        """
        Assures it raises an exception when given a war that doesn't exist yet.
        """
        conn = valid_labels_fixture.get_connection()

        ticket_with_bad_war = Ticket(
            VALID_WAR.war_number + 1,
            *VALID_TICKETS[1][1:]
        )

        with pytest.raises(data.CannotCreateTicketForWarException):
            ticket_id = data.tickets.insert_ticket(
                ticket_with_bad_war,
                conn
            )

    def test_raises_exception_for_fake_map(self, valid_labels_fixture):
        """Assures it raises an exception for a map which doesn't exist."""
        conn = valid_labels_fixture.get_connection()

        ticket_with_fake_map = Ticket(
            VALID_TICKETS[0].war_number,
            "NonsenseFakeHex",
            *VALID_TICKETS[0][2:]
        )

        with pytest.raises(data.tickets.MapDoesNotExistException):
            ticket_id = data.tickets.insert_ticket(
                ticket_with_fake_map,
                conn
            )


class TestSelectTicket:
    def test_select_ticket_with_origin_which_exists(self, valid_labels_fixture):
        conn = valid_labels_fixture.get_connection()

        ticket_id = data.tickets.insert_ticket(VALID_TICKETS[1], conn)

        assert data.tickets.select_ticket(ticket_id, conn) == VALID_TICKETS[1]

    def test_select_ticket_without_origin_which_exists(
        self,
        valid_labels_fixture
    ):
        conn = valid_labels_fixture.get_connection()

        ticket_id = data.tickets.insert_ticket(VALID_TICKETS[0], conn)

        assert data.tickets.select_ticket(ticket_id, conn) == VALID_TICKETS[0]

    def test_raises_exception_when_ticket_id_does_not_exist(
        self,
        valid_labels_fixture
    ):
        conn = valid_labels_fixture.get_connection()

        with pytest.raises(Exception):
            result = data.tickets.select_ticket(999999999, conn)
        
    
