import os
import logging

logging.getLogger("supabase_py").setLevel(logging.WARNING)
log = logging.getLogger("supabase_py")

from supabase_py import create_client, Client
from dotenv import load_dotenv

load_dotenv()

supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_ANON"))  # type: ignore

SUPA_TABLE = "operational_rails_dev"


def write_to_supabase(data, source_id):
    """Write data to Supabase"""
    try:
        # Flatten the usage dictionary
        payload = {
            "id": data["id"],
            "object": data["object"],
            "model": data["model"],
            "prompt_tokens": data["usage"]["prompt_tokens"],
            "completion_tokens": data["usage"]["completion_tokens"],
            "total_tokens": data["usage"]["total_tokens"],
            "finish_reason": data["choices"][0]["finish_reason"],
            "source_id": source_id,
        }

        response = supabase.table(SUPA_TABLE).insert(payload).execute()  # type: ignore

        if "status_code" in response and response["status_code"] == 201:
            log.info("Successfully wrote to Supabase, response: %s", response["data"])
            return True
        else:
            log.error(
                "Failed to write to Supabase, status code: %s, error: %s",
                response.get("status_code"),
                response.get("error_message"),
            )
            return False

    except Exception as err:
        log.error("Failed to write to Supabase, error: %s, data: %s", err, data)
        return False
