from openai import OpenAI
from django.conf import settings

# Initialize OpenAI client with API key from settings
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_answer(prompt):
    """
    Generate an AI-powered tutoring answer.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",   # you can change to gpt-5 if enabled
            messages=[
                {"role": "system", "content": "You are a helpful tutor."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.6
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"
