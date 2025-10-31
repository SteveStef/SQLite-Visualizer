import os
import boto3
from database_conn import get_database_schema
from dotenv import load_dotenv
load_dotenv()

class Bedrock():
    def __init__(self):
        self.model_id = "amazon.nova-lite-v1:0"
        self.client = client = boto3.client(
            service_name="bedrock-runtime",
            region_name="us-east-1"
        )

    def check_health(self) -> bool:
        try:
            response = self.client.converse(
                modelId=self.model_id,
                messages=[{"role": "user", "content": [{"text": "test"}]}],
                inferenceConfig={"maxTokens": 10, "temperature": 0}
            )
            return True
        except Exception as e:
            raise Exception(f"Bedrock health check failed: {str(e)}")

    def get_sql(self, text, schema) -> str:
      system_prompt = f"""You are an expert SQLite assistant for SQLite databases.

{schema}

Note that all commands must be valid commands for SQLite not MYSQL or POSTGRESQL.

If the user's input requires a database query, generate ONLY the SQL query needed to answer their question.
Do not include explanations, markdown, back ticks, sql preference header, or code blocks - just the raw SQL query.

CRITICAL RULES:
1. NEVER use placeholder values like 'your_user_id', 'example_value', 'user_id_here', etc.
2. If the user says "the user" or "the one user" and context suggests there's only one row, omit the WHERE clause entirely to update all rows.
3. If the user doesn't provide enough information to identify a specific row (like an ID or unique value), return:
   NO_QUERY_NEEDED

If the user's input does NOT require a database query (e.g., greetings, general questions, help requests), respond with exactly:
NO_QUERY_NEEDED"""
      response = self.client.converse(
          modelId=self.model_id,
          system=[{"text": system_prompt}],
          messages=[{"role": "user", "content": [{"text": text}]}],
          inferenceConfig={"maxTokens": 500, "temperature": 0}
      )

      return response['output']['message']['content'][0]['text'].strip()

if __name__ == "__main__":
    b = Bedrock()
    a = b.get_sql("Hello World","")
    print(a)

