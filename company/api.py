from __future__ import annotations
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from company.models import (
    Agent,
    Team,
    Ticket,
    Meeting,
    Role,
    Level,
    TeamType,
    TicketStatus,
    TicketPriority,
    MeetingType,
)
from company.cli import store, create_agent, create_team, create_ticket, assign_ticket, update_ticket_status, create_meeting, attend_meeting, add_meeting_report, list_teams, list_tickets, list_meetings, get_progress, serialize
import uuid


class APIHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, default=serialize).encode())

    def _get_json(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            body = self.rfile.read(content_length)
            return json.loads(body.decode())
        return {}

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path

        if path == "/health":
            self._send_json({"status": "ok"})
        elif path == "/api/agents":
            agents = list(store.agents.values())
            self._send_json([serialize(a) for a in agents])
        elif path == "/api/teams":
            teams = list_teams()
            self._send_json([serialize(t) for t in teams])
        elif path == "/api/tickets":
            status = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("status", [None])[0]
            ticket_status = TicketStatus(status) if status else None
            tickets = list_tickets(ticket_status)
            self._send_json([serialize(t) for t in tickets])
        elif path == "/api/meetings":
            meetings = list_meetings()
            self._send_json([serialize(m) for m in meetings])
        elif path == "/api/progress":
            progress = get_progress()
            self._send_json(progress)
        elif path.startswith("/api/agents/"):
            agent_id = path.split("/")[-1]
            agent = store.agents.get(agent_id)
            if not agent:
                self._send_json({"error": "Agent not found"}, 404)
            else:
                self._send_json(serialize(agent))
        elif path.startswith("/api/teams/"):
            team_id = path.split("/")[-1]
            team = store.teams.get(team_id)
            if not team:
                self._send_json({"error": "Team not found"}, 404)
            else:
                self._send_json(serialize(team))
        elif path.startswith("/api/tickets/"):
            parts = path.split("/")
            if len(parts) >= 4:
                ticket_id = parts[2]
                ticket = store.tickets.get(ticket_id)
                if not ticket:
                    self._send_json({"error": "Ticket not found"}, 404)
                else:
                    self._send_json(serialize(ticket))
        elif path.startswith("/api/meetings/"):
            parts = path.split("/")
            if len(parts) >= 4:
                meeting_id = parts[2]
                meeting = store.meetings.get(meeting_id)
                if not meeting:
                    self._send_json({"error": "Meeting not found"}, 404)
                else:
                    self._send_json(serialize(meeting))
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        data = self._get_json()

        if path == "/api/agents":
            role = Role(data.get("role", "developer"))
            level = Level(data.get("level", 1))
            agent = create_agent(
                agent_id=data.get("id", str(uuid.uuid4())),
                role=role,
                level=level,
                team_id=data.get("team_id"),
                boss_id=data.get("boss_id"),
            )
            self._send_json(serialize(agent), 201)
        elif path == "/api/teams":
            team_type = TeamType(data.get("type", "engineering"))
            team = create_team(
                team_id=data.get("id", str(uuid.uuid4())),
                team_type=team_type,
                leader_id=data["leader_id"],
            )
            self._send_json(serialize(team), 201)
        elif path == "/api/tickets":
            priority = TicketPriority(data.get("priority", "medium"))
            ticket = create_ticket(
                ticket_id=data.get("id", str(uuid.uuid4())),
                priority=priority,
            )
            self._send_json(serialize(ticket), 201)
        elif path == "/api/meetings":
            meeting_type = MeetingType(data.get("type", "daily_standup"))
            meeting = create_meeting(
                meeting_id=data.get("id", str(uuid.uuid4())),
                meeting_type=meeting_type,
                leader_id=data["leader_id"],
            )
            self._send_json(serialize(meeting), 201)
        elif path.startswith("/api/tickets/") and path.endswith("/assign"):
            ticket_id = path.split("/")[2]
            agent_id = data.get("agent_id")
            if not agent_id:
                self._send_json({"error": "agent_id required"}, 400)
            else:
                ticket = assign_ticket(ticket_id, agent_id)
                self._send_json(serialize(ticket))
        elif path.startswith("/api/meetings/") and path.endswith("/attend"):
            meeting_id = path.split("/")[2]
            agent_id = data.get("agent_id")
            if not agent_id:
                self._send_json({"error": "agent_id required"}, 400)
            else:
                meeting = attend_meeting(meeting_id, agent_id)
                self._send_json(serialize(meeting))
        elif path.startswith("/api/meetings/") and "/reports" in path:
            meeting_id = path.split("/")[2]
            author_id = data.get("author_id")
            content = data.get("content")
            if not author_id or not content:
                self._send_json({"error": "author_id and content required"}, 400)
            else:
                meeting = add_meeting_report(meeting_id, author_id, content)
                self._send_json(serialize(meeting))
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_PUT(self):
        path = urllib.parse.urlparse(self.path).path
        data = self._get_json()

        if path.startswith("/api/tickets/") and path.endswith("/status"):
            ticket_id = path.split("/")[2]
            status = data.get("status")
            if not status:
                self._send_json({"error": "status required"}, 400)
            else:
                ticket = update_ticket_status(ticket_id, TicketStatus(status))
                self._send_json(serialize(ticket))
        else:
            self._send_json({"error": "Not found"}, 404)

    def log_message(self, format, *args):
        pass


def run_api(host="0.0.0.0", port=5000):
    server = HTTPServer((host, port), APIHandler)
    print(f"API server running on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_api()
