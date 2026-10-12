"""Guava inbound entrypoint."""

import os

import guava
from guava import logging_utils

from technician_assistant.agent import create_agent

PHONE_NUMBER = "+12402122724"


def main() -> None:
    """Serve phone and optional WebRTC channels."""
    logging_utils.configure_logging()
    agent = create_agent()
    runner = guava.Runner().listen_phone(agent, PHONE_NUMBER)
    webrtc_code = os.getenv("GUAVA_WEBRTC_CODE", "").strip()
    if webrtc_code:
        runner.listen_webrtc(agent, webrtc_code)
    runner.run()


if __name__ == "__main__":
    main()