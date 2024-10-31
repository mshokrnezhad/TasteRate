from openai import OpenAI

client = OpenAI(
    api_key="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",
)


def chat_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


response = chat_gpt("hello!")
print(response)
