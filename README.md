# Database Browser with AI

A terminal-based SQLite database browser with AI-powered natural language query generation using AWS Bedrock.

## Features

- **SQLite Database Browser** - View tables, browse data, and inspect rows
- **AI-Powered Queries** - Ask questions in plain English, get SQL automatically
- **Dual Mode** - Switch between AI mode and direct SQL mode
- **Safe Modifications** - Confirmation required before committing data changes (UPDATE/DELETE/INSERT)
- **Professional Dark Theme** - Eye-friendly terminal UI
- **Keyboard Navigation** - Full keyboard support with intuitive bindings


## Installation

### Prerequisites

- Python 3.8+
- uv (Python package manager)
- AWS Account with Bedrock access

### Setup

1. **Clone or download the project**
   ```bash
   cd /path/to/dbui
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Configure AWS Bedrock API Key**

   a. Visit the AWS Bedrock API Keys page:
   ```
   https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/api-keys?tab=short-term
   ```

   b. Click **"Generate API Key"** to create a short-term key

   c. Copy the generated bearer token

   d. Create a `.env` file in the project root:
   ```bash
   touch .env
   ```

   e. Add your API key to `.env`:
   ```env
   AWS_BEARER_TOKEN_BEDROCK=bedrock-api-key-YOUR_TOKEN_HERE
   ```

   **Important:** Never commit your `.env` file to git!

4. **Verify `.gitignore` includes `.env`**
   ```bash
   echo ".env" >> .gitignore
   ```

## Usage

### Basic Usage

```bash
uv run app.py /path/to/your/database.db
```

Example:
```bash
uv run app.py ./example.db
```

### AI Mode (Natural Language Queries)

1. Press `t` to switch to **AI Mode** (? icon)
2. Type your question in plain English:
   - "Show me all users from California"
   - "Count total orders by month"
   - "Find products with low stock"
3. Press Enter - the AI generates and executes SQL automatically

### SQL Mode (Direct Queries)

1. Press `t` to switch to **SQL Mode** (=? icon)
2. Type raw SQL queries:
   ```sql
   SELECT * FROM users WHERE state = 'CA'
   ```
3. Press Enter to execute

### Data Modification Safety

When using UPDATE, DELETE, or INSERT queries (especially in AI mode):
1. Query executes but **does NOT commit** immediately
2. Shows number of rows affected
3. Prompts: "Press 'y' to commit or 'n' to cancel"
4. Press `y` to save changes permanently
5. Press `n` to rollback (no changes made)

## Key Bindings

| Key | Action |
|-----|--------|
| `Tab` | Switch between table and input field |
| `t` | Toggle between AI Mode and SQL Mode |
| `b` | Go back to table list (when viewing table data) |
| `y` | Confirm data changes (when prompted) |
| `n` | Cancel data changes (when prompted) |
| `q` | Quit application |

## Modes

### ? AI Mode
- Ask questions in natural language
- AI converts to SQL automatically
- Shows generated SQL query
- Confirms before modifying data

### =? SQL Mode
- Write SQL queries directly
- Full SQLite syntax support
- Immediate execution (SELECT queries)
- Confirms before modifying data

## Features in Detail

### Schema Inspection
```sql
-- See table structure
PRAGMA table_info(table_name);

-- See CREATE statement
SELECT sql FROM sqlite_master WHERE name = 'table_name';
```

### Query Results
- **SELECT** queries display formatted JSON results
- **UPDATE/DELETE/INSERT** show affected row counts
- Schema queries show formatted CREATE statements
- Scrollable panels for large result sets

### Error Handling
- SQL syntax errors displayed in left panel
- AI initialization failures show clear error messages
- Connection issues handled gracefully

## Troubleshooting

### "AI assistant not initialized"
**Solution:** Check your `.env` file has the correct `AWS_BEARER_TOKEN_BEDROCK` value

### "Bedrock health check failed"
**Causes:**
- Expired API key (short-term keys expire after ~12 hours)
- Invalid bearer token
- No internet connection
- AWS Bedrock not available in your region

**Solution:** Generate a new API key from the AWS Console

### "Unable to interpret a database query from this request"
**Cause:** AI couldn't determine what SQL query to generate

**Solution:** Be more specific, e.g.:
- L "update the user"
-  "update user with id 5 to have state DE"

### Database file errors
**Cause:** Invalid database path or file not found

**Solution:** Ensure you provide an absolute path to a `.db` file:
```bash
uv run app.py /absolute/path/to/database.db
```

## Security Notes

? **Important Security Practices:**

1. **Never commit `.env` to version control**
   - Add `.env` to `.gitignore`
   - Use `.env.example` for templates

2. **Short-term API keys expire**
   - AWS Bedrock short-term keys typically expire after 12 hours
   - Regenerate as needed

3. **Database backups**
   - Always backup your database before using UPDATE/DELETE
   - Test queries on a copy first

4. **SQL injection awareness**
   - The AI generates SQL from your natural language
   - Review generated SQL before confirming data modifications

## Contributing

This is a personal project. Feel free to fork and modify for your own use.

## License

See project license file.

## Acknowledgments

- Built with [Textual](https://textual.textualize.io/) - TUI framework
- Powered by [AWS Bedrock](https://aws.amazon.com/bedrock/) - AI/LLM service
- Uses Amazon Nova Lite model for SQL generation
