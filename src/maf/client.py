# client.py
"""
Shared AzureOpenAIResponsesClient for the Next.js Stitch pipeline.

Authentication priority:
  - Local dev:   AzureCliCredential (requires `az login`)
  - Production:  DefaultAzureCredential (managed identity / env vars)

Required environment variables (set in .env):
  AZURE_OPENAI_ENDPOINT     - e.g. https://<name>.openai.azure.com/
  AZURE_OPENAI_DEPLOYMENT   - default model deployment (e.g. gpt-4o)
  AZURE_OPENAI_API_VERSION  - API version (e.g. 2025-01-01-preview)

Optional:
  AZURE_OPENAI_FAST_DEPLOYMENT - lightweight model (e.g. gpt-4o-mini)
  AZURE_OPENAI_API_KEY         - explicit key; omit to use credential-based auth
"""
import os

from azure.identity import AzureCliCredential, DefaultAzureCredential
from dotenv import load_dotenv

from agent_framework.azure import AzureOpenAIResponsesClient

load_dotenv()


def get_client(use_managed_identity: bool = False) -> AzureOpenAIResponsesClient:
    """
    Return a configured AzureOpenAIResponsesClient.

    Args:
        use_managed_identity: When True, use DefaultAzureCredential (for
                              production / managed identity environments).
                              When False (default), use AzureCliCredential
                              (requires `az login` locally).
    """
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    if not endpoint:
        raise EnvironmentError(
            "AZURE_OPENAI_ENDPOINT is not set. "
            "Create a .env file with AZURE_OPENAI_ENDPOINT=https://<name>.openai.azure.com/"
        )

    api_key = os.environ.get("AZURE_OPENAI_API_KEY")

    if api_key:
        # Key-based auth (dev convenience — prefer credential-based in production)
        return AzureOpenAIResponsesClient(
            endpoint=endpoint,
            api_key=api_key,
            deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2025-01-01-preview"),
        )

    credential = DefaultAzureCredential() if use_managed_identity else AzureCliCredential()
    return AzureOpenAIResponsesClient(
        credential=credential,
        endpoint=endpoint,
        deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2025-01-01-preview"),
    )


# Singleton used throughout the project.
# Pass use_managed_identity=True via env override for production:
_use_mi = os.environ.get("USE_MANAGED_IDENTITY", "").lower() in ("1", "true", "yes")
client = get_client(use_managed_identity=_use_mi)
