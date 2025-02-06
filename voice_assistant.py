#!/usr/bin/env python3

"""
A simple voice assistant using ElevenLabs Conversational AI.
This application creates an interactive voice conversation with an AI agent.
"""

import os
import signal
import sys
import logging
from typing import Optional
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation, ClientTools
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface
import json
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VoiceAssistant:
    """
    A voice assistant class that manages conversations with ElevenLabs AI agent.
    Supports conversation history, volume control, and configurable timeouts.
    """
    
    def __init__(self):
        """Initialize the voice assistant with configuration from environment variables."""
        load_dotenv()  # Load environment variables from .env file
        
        # Required configuration
        self.agent_id = os.getenv("AGENT_ID")
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        
        if not self.agent_id:
            raise ValueError("AGENT_ID environment variable is required")
        
        # Optional configuration
        self.volume = float(os.getenv("VOLUME", "1.0"))
        self.timeout = int(os.getenv("TIMEOUT", "300"))  # 5 minutes default
        
        # Initialize state
        self.conversation: Optional[Conversation] = None
        self.client = ElevenLabs(api_key=self.api_key)
        self.history = []
        self.start_time = None
        
    def save_conversation(self, filename: Optional[str] = None) -> None:
        """
        Save the conversation history to a file.
        
        Args:
            filename: Optional custom filename, defaults to timestamp-based name
        """
        if not self.history:
            return
            
        if filename is None:
            # Create logs directory if it doesn't exist
            Path("logs").mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"logs/conversation_{timestamp}.json"
            
        with open(filename, "w") as f:
            json.dump({
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": datetime.now().isoformat(),
                "history": self.history
            }, f, indent=2)
            
        logger.info(f"Conversation saved to {filename}")

    def agent_response_callback(self, response: str) -> None:
        """Callback for handling agent responses."""
        self.history.append({
            "role": "agent",
            "text": response,
            "timestamp": datetime.now().isoformat()
        })
        logger.info(f"Agent: {response}")
        
    def user_transcript_callback(self, transcript: str) -> None:
        """Callback for handling user speech transcripts."""
        self.history.append({
            "role": "user",
            "text": transcript,
            "timestamp": datetime.now().isoformat()
        })
        logger.info(f"User: {transcript}")
        
    def correction_callback(self, original: str, corrected: str) -> None:
        """Callback for handling response corrections."""
        logger.info(f"Correction: '{original}' → '{corrected}'")
        
    def latency_callback(self, latency: float) -> None:
        """Callback for monitoring system latency."""
        logger.debug(f"Latency: {latency}ms")
        
    def handle_interrupt(self, signum, frame) -> None:
        """Handle interrupt signals gracefully."""
        logger.info("\nReceived interrupt signal. Ending conversation...")
        if self.conversation:
            self.conversation.end_session()
            
    def setup_client_tools(self) -> ClientTools:
        """
        Set up client-side tools that the AI agent can use.
        
        Returns:
            ClientTools: Configured client tools instance
        """
        def log_message(parameters: dict) -> None:
            """
            Client tool to log messages from the AI agent.
            
            Args:
                parameters: Dictionary containing the message parameter
            """
            message = parameters.get("message")
            if message:
                logger.info(f"AI Tool Call - Log Message: {message}")
        
        client_tools = ClientTools()
        client_tools.register("logMessage", log_message)
        return client_tools

    def start(self) -> None:
        """Start the voice assistant conversation."""
        try:
            # Set up signal handler for graceful shutdown
            signal.signal(signal.SIGINT, self.handle_interrupt)
            
            self.start_time = datetime.now()
            
            # Initialize client tools
            client_tools = self.setup_client_tools()
            
            # Initialize the conversation
            self.conversation = Conversation(
                client=self.client,
                agent_id=self.agent_id,
                requires_auth=bool(self.api_key),
                audio_interface=DefaultAudioInterface(),
                callback_agent_response=self.agent_response_callback,
                callback_user_transcript=self.user_transcript_callback,
                callback_agent_response_correction=self.correction_callback,
                callback_latency_measurement=self.latency_callback,
                volume=self.volume,
                client_tools=client_tools
            )
            
            logger.info("Starting conversation. Press Ctrl+C to end.")
            self.conversation.start_session()
            
            # Wait for the conversation to end
            conversation_id = self.conversation.wait_for_session_end()
            logger.info(f"Conversation ended. ID: {conversation_id}")
            
            # Save conversation history
            self.save_conversation()
            
        except Exception as e:
            logger.error(f"Error during conversation: {e}")
            if self.conversation:
                self.conversation.end_session()
            self.save_conversation("logs/conversation_error.json")
            sys.exit(1)

def main():
    """Main entry point for the voice assistant application."""
    try:
        assistant = VoiceAssistant()
        assistant.start()
    except KeyboardInterrupt:
        logger.info("\nApplication terminated by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 