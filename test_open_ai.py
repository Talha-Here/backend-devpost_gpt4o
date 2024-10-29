import os
from dotenv import load_dotenv
from openai import OpenAI

# for checking if open ai key is working or not
# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from the environment variable
openai_key = os.getenv("openAI_key")

print(openai_key)
# Initialize OpenAI client
client = OpenAI(api_key=openai_key)


def test_openai_connection():
    try:
        # Making a simple request to the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello, OpenAI!"}],
            max_tokens=5
        )

        # Print the response
        print("Connection successful! Response:")
        print(response.choices[0].message.content)
    except Exception as e:
        print("Failed to connect to OpenAI API:")
        print(str(e))


if __name__ == "__main__":
    test_openai_connection()
