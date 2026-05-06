from vertexai.generative_models import GenerativeModel
from dotenv import load_dotenv
from anthropic import AnthropicVertex
import os
from openai import OpenAI
from src.text_generation.vertexai_setup import initialize_vertexai_params, get_default_config
from huggingface_hub import InferenceClient

# Load environment variables
load_dotenv()
OAI_API_KEY = os.getenv("OPENAI_API_KEY")


def _validate_tokens(max_tokens: int) -> int:
    """
    Validates the max_tokens parameter. Ensures it's within a valid range (1 to 8192).
    If invalid, defaults to 8192.
    """
    if 1 <= max_tokens <= 8192:
        return max_tokens
    return 8192


def _validate_temperature(temp: float) -> float:
    """
    Validates the temperature parameter. Ensures it's within a valid range (0 to 1).
    If invalid, defaults to 0.49.
    """
    if 0 <= temp <= 1:
        return temp
    return 0.49


class LLMBaseClass:
    """
    Base class for text generation. Users provide the HF model ID or other model identifiers
    and can call the generate method to get responses.
    """

    def __init__(self, model_id: str, max_tokens: int, temp: float) -> None:
        self.model_id = model_id
        self.api_key = None
        self.temp = _validate_temperature(temp)
        self.tokens = _validate_tokens(max_tokens)
        self.model = self._initialize_model()

    def _initialize_model(self):
        """
        Initialize the model based on the provided model ID.
        """
        if self.model_id == "gpt-4o-mini":
            return self._initialize_openai_model()
        elif self.model_id == "claude-3-5-sonnet@20240620":
            return self._initialize_claude_model()
        elif self.model_id in ["claude-3-5-sonnet@20240620",
                               "gemini-1.0-pro", "gemini-1.5-flash-001", "gemini-2.5-flash"]:
            return self._initialize_vertexai_model()
        else:
            return self._initialize_hf_model()

    def _initialize_openai_model(self):
        """
        Initialize OpenAI model.
        """
        self.api_key = OAI_API_KEY
        return OpenAI(api_key=self.api_key)

    def _initialize_claude_model(self):
        """
        Initialize Claude model using Anthropic via Vertex AI.
        """
        self.api_key = os.getenv("VERTEXAI_PROJECTID")
        return AnthropicVertex(region="europe-west1", project_id=self.api_key)

    def _initialize_vertexai_model(self):
        """
        Initialize Google Gemini model using Vertex AI.
        """
        default_gen_config, default_safe_settings = get_default_config()
        gen_config = {
            "temperature": self.temp,
            "max_output_tokens": self.tokens,
        }
        return GenerativeModel(self.model_id,
                               generation_config=default_gen_config if gen_config is None else gen_config,
                               safety_settings=default_safe_settings)

    def _initialize_hf_model(self):
        self.api_key = os.getenv("HF_TOKEN")
        return InferenceClient(token=self.api_key, model=self.model_id)

    def generate(self, messages):
        """
        Generate responses based on the model type and provided messages.
        """
        if self.model_id == "gpt-4o-mini":
            return self._generate_openai(messages)
        elif self.model_id in ["claude-3-5-sonnet@20240620",
                               "gemini-1.0-pro", "gemini-1.5-flash-001", "gemini-2.5-flash"]:
            return self._generate_vertexai(messages)
        else:
            return self._generate_hf(messages)

    def _generate_openai(self, messages):
        """
        Generate responses using OpenAI model.
        """
        completion = self.model.chat.completions.create(
            model=self.model_id,
            messages=messages,
            temperature=self.temp,
            max_tokens=self.tokens,
        )
        return completion.choices[0].message.content

    def _generate_vertexai(self, messages):
        """
        Generate responses using Claude or Gemini models via Vertex AI.
        """
        initialize_vertexai_params()
        content = " ".join([message["content"] for message in messages])
        if "claude" in self.model_id:
            message = self.model.messages.create(
                max_tokens=self.tokens,
                model=self.model_id,
                messages=[{"role": "user", "content": content}],
            )
            return message.content[0].text
        else:
            response = self.model.generate_content(content)
            return response.text

    def _generate_hf(self, messages):
        """
        Generate responses using Hugging Face models.
        """
        content = " ".join([message["content"] for message in messages])
        response = self.model.chat_completion(
            messages=[{"role": "user", "content": messages[0]["content"] + messages[1]["content"]}],
            max_tokens=self.tokens, temperature=self.temp)
        return response.choices[0].message.content
