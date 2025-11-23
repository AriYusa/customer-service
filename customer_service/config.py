"""Configuration module for the customer service agent."""

import logging
import os

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class AgentModel(BaseModel):
    """Agent model settings."""

    name: str = Field(default="customer_service_coordinator")
    # model: str = Field(default="gemini-2.5-flash")
    model: str = Field(default="anthropic/claude-3-7-sonnet-20250219")


class Config(BaseSettings):
    """Configuration settings for the customer service agent."""

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.env"),
        env_prefix="GOOGLE_",
        case_sensitive=True,
        extra="ignore",
    )
    agent_settings: AgentModel = Field(default=AgentModel())
    app_name: str = "customer_service_app"
    CLOUD_PROJECT: str = Field(default="my_project")
    CLOUD_LOCATION: str = Field(default="us-central1")
    GENAI_USE_VERTEXAI: str = Field(default="1")
    API_KEY: str | None = Field(default="")
    ANTHROPIC_API_KEY: str | None = Field(default="", env_prefix="")
    OPENAI_API_KEY: str | None = Field(default="", env_prefix="")

    def get_model_for_agent(self, model_override: str | None = None):
        """Get the model configuration for an agent.
        
        If the model name starts with 'anthropic/' or 'openai/', wraps it with LiteLlm.
        Otherwise returns the model name directly for use with Gemini.
        
        Args:
            model_override: Optional model override string.
            
        Returns:
            Either a string (for Gemini) or LiteLlm instance (for other providers).
        """
        from google.adk.models.lite_llm import LiteLlm
        
        model_name = model_override or self.agent_settings.model
        
        # Check if it's an Anthropic or OpenAI model
        if model_name.startswith(("anthropic/", "openai/")):
            return LiteLlm(model=model_name)
        
        # Default to returning the model name as-is (for Gemini)
        return model_name
