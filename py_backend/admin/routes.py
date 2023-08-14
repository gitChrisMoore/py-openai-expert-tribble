import json
from dotenv import load_dotenv
from flask import Response, jsonify
from py_backend.admin import bp
from py_backend.storage.db_setup import initialize_database
from py_backend.bots.AIThreadManager import thread_manager

load_dotenv()


@bp.route("/reset_database", methods=["GET"])
def reset_database():
    """Reset the database and initialize it with the default data."""
    try:
        initialize_database()
        response = {
            "success": True,
            "message": "Database has been successfully reset and initialized.",
        }
        return Response(
            json.dumps(response), content_type="application/json", status=200
        )
    except Exception as error:
        # Here, you can log the error if needed
        print(f"An error occurred while resetting the database: {str(error)}")
        response = {
            "success": False,
            "message": f"Failed to reset the database: {str(error)}",
        }
        return Response(
            json.dumps(response), content_type="application/json", status=500
        )


@bp.route("/threads_status")
def threads_status():
    """Returns the status of all threads."""
    status = thread_manager.get_status()
    return jsonify(status), 200


@bp.route("/restart_threads")
def restart_threads():
    """Restarts all threads."""
    thread_manager.start_threads()
    return jsonify(message="Threads restarted"), 200
