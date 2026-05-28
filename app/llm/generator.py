import os

from dotenv import load_dotenv
from openai import OpenAI

from app.llm.prompts import SYSTEM_PROMPT, DENOMINATION_PROMPTS

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY"),
)


def generate_response(question, verses, denomination, history):
    context = "\n\n".join([
        f'{v["citation"]}: {v["text"]}' for v in verses
    ]) if verses else "No specific verses retrieved."

    denomination_note = DENOMINATION_PROMPTS.get(denomination, "")
    system = SYSTEM_PROMPT
    if denomination_note:
        system += f"\n\nDenomination context: {denomination_note}"

    messages = [{"role": "system", "content": system}]

    for turn in history[-5:]:
        messages.append({"role": "user", "content": turn["question"]})
        messages.append({"role": "assistant", "content": turn["response"]})

    messages.append({
        "role": "user",
        "content": (
            f"Retrieved Scripture Context:\n{context}\n\n"
            f"Question: {question}"
        )
    })

    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=messages,
        temperature=0.4,
    )

    return response.choices[0].message.content
