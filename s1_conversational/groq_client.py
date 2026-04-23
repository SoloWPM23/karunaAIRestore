# s1_conversational/groq_client.py

from groq import Groq #type: ignore
from dotenv import load_dotenv
import os
import threading

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
_CLIENT_LOCK = threading.Lock()

# Model default - bisa diganti sesuai kebutuhan
DEFAULT_MODEL = "llama-3.3-70b-versatile"


def generate_content_safe(
    *,
    model: str,
    system_prompt: str,
    messages: list,
    max_tokens: int = 8000,
    temperature: float = 0.8,
):
    """
    Wrapper thread-safe untuk mencegah race saat banyak sesi memanggil Groq bersamaan.

    Args:
        model: Nama model Groq (e.g., "llama-3.3-70b-versatile")
        system_prompt: System instruction untuk model
        messages: List of messages dalam format ChatML [{"role": "user/assistant", "content": "..."}]
        max_tokens: Maximum output tokens
        temperature: Temperature untuk sampling

    Returns:
        Response text dari model
    """
    # Build full messages dengan system prompt
    full_messages = [{"role": "system", "content": system_prompt}] + messages

    with _CLIENT_LOCK:
        response = client.chat.completions.create(
            model=model,
            messages=full_messages,
            temperature=temperature,
            max_completion_tokens=max_tokens,
            top_p=1,
            stream=False,
        )
        return response.choices[0].message.content or ""


def chat_with_groq(system_prompt: str, history: list, user_message: str) -> str:
    """
    Kirim chat ke Groq dengan system prompt dan history.

    Args:
        system_prompt: System instruction
        history: Riwayat percakapan dalam format [{"role": "user/assistant", "content": "..."}]
        user_message: Pesan terbaru dari user

    Returns:
        Response text dari model
    """
    # Convert history ke format ChatML jika belum
    messages = []
    for msg in history:
        if isinstance(msg, dict):
            messages.append(msg)
        else:
            # Handle legacy format jika ada
            messages.append({"role": msg.get("role", "user"), "content": str(msg)})

    # Tambah pesan user terbaru
    messages.append({"role": "user", "content": user_message})

    return generate_content_safe(
        model=DEFAULT_MODEL,
        system_prompt=system_prompt,
        messages=messages,
        max_tokens=8000,
        temperature=0.8,
    )
