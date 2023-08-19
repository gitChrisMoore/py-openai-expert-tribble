import logging
import threading
from py_backend.bots.ceo_advisor_ai import run_ceo_advisor_ai
from py_backend.bots.ceo_trend_ai import run_trend_ai


logging.getLogger("AIThreadManager").setLevel(logging.WARNING)
log = logging.getLogger("AIThreadManager")


class AIThreadManager:
    """Manages the AI threads."""

    def __init__(self, initial_threads=None):
        """Initialize the manager and optionally add threads.

        Args:
            initial_threads (list): List of tuples where each tuple is (thread_name, thread_function).
        """
        if initial_threads is None:
            initial_threads = [
                # ("CEO Advisor AI", run_ceo_advisor_ai),
                # ("CEO Trend AI", run_trend_ai),
                # ("Persona AI Two", run_droid),
            ]

        self.threads = []
        self.add_threads(initial_threads)

    def add_threads(self, thread_data):
        """Add threads without starting them.

        Args:
            thread_data (list): List of tuples where each tuple is (thread_name, thread_function).
        """

        for name, target, args in thread_data:
            self.threads.append(threading.Thread(name=name, target=target, args=args))

    def start_threads(self):
        """Starts all threads that aren't already running."""
        all_started_successfully = True  # Flag to track thread start status

        print(f"Starting threas: {self.threads}")
        for thread in self.threads:
            if not thread.is_alive():
                try:
                    print(f"Starting thread {thread.name}")
                    thread.start()
                except threading.ThreadError as err:
                    all_started_successfully = False  # Update flag on exception
                    logging.error(f"Failed to start thread {thread.name}: {err}")
                except Exception as err:
                    all_started_successfully = False  # Update flag on exception
                    logging.error(
                        f"Unexpected error occurred while starting thread {thread.name}: {err}"
                    )

        if all_started_successfully:
            logging.info(
                "All threads started successfully without any errors or exceptions."
            )

    def stop_threads(self):
        """Stops all threads."""
        for thread in self.threads:
            if thread.is_alive():
                thread.join(0)

    def get_status(self):
        """Returns the status of all threads."""
        return [
            {"thread_name": thread.name, "thread_status": thread.is_alive()}
            for thread in self.threads
        ]


thread_manager = AIThreadManager()
