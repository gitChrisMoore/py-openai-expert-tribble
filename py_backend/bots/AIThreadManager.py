import threading
from py_backend.bots.ceo_advisor_ai import run_ceo_advisor_ai
from py_backend.bots.ceo_trend_ai import run_trend_ai
from py_backend.bots.persona_ai_two import run_persona_ai_two


class AIThreadManager:
    """Manages the AI threads."""

    def __init__(self):
        self.threads = []

    def start_threads(self):
        """Starts all threads."""
        if self.threads:
            self.stop_threads()

        named_threads = [
            ("CEO Advisor AI", run_ceo_advisor_ai),
            ("CEO Trend AI", run_trend_ai),
            ("Persona AI Two", run_persona_ai_two),
        ]

        self.threads = [
            threading.Thread(name=name, target=target) for name, target in named_threads
        ]

        for thread in self.threads:
            thread.start()

    def stop_threads(self):
        """Stops all threads."""
        for thread in self.threads:
            thread.join(0)

        self.threads = []

    def get_status(self):
        """Returns the status of all threads."""
        return [
            {"thread_name": thread.name, "thread_status": thread.is_alive()}
            for thread in self.threads
        ]


thread_manager = AIThreadManager()
