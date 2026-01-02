# CliftonStrengths Profile Agent

A LangGraph agent for managing employee CliftonStrengths profiles. This agent stores and retrieves complete CliftonStrengths assessments (all 34 themes) using AWS DynamoDB.

## What It Does

The CliftonStrengths Agent helps you:

- **Store profiles**: Save employee CliftonStrengths data (name, email, and all 34 ranked strengths)
- **Retrieve profiles**: Look up profiles by first and last name
- **Handle duplicates**: Returns all profiles when multiple employees share the same name

The agent uses conversational AI to interact naturally while managing profile data in DynamoDB.

## Quick Start

### Prerequisites

- Python 3.11 or higher
- AWS account with DynamoDB access
- Anthropic API key (or OpenAI)

### Setup

1. **Install dependencies**

```bash
# Activate virtual environment
source /path/to/.venv/bin/activate

# Install the package
pip install -e .
```

2. **Configure environment variables**

Create a `.env` file in the project root:

```bash
# Required: LLM API Key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Required: AWS Configuration
AWS_REGION=us-east-1
AWS_PROFILE=your-aws-profile-name
DYNAMODB_TABLE_NAME=profiles

# Optional: LangSmith Tracing
LANGSMITH_API_KEY=your-langsmith-key
LANGSMITH_PROJECT=strengths-agent
```

3. **Create DynamoDB table**

The `profiles` table requires:
- Primary key: `email_address` (String)
- Global Secondary Index: `name-index` with `first_name` (partition key) and `last_name` (sort key)

```bash
aws dynamodb create-table \
  --table-name profiles \
  --attribute-definitions \
    AttributeName=email_address,AttributeType=S \
    AttributeName=first_name,AttributeType=S \
    AttributeName=last_name,AttributeType=S \
  --key-schema AttributeName=email_address,KeyType=HASH \
  --global-secondary-indexes \
    '[{"IndexName":"name-index","KeySchema":[{"AttributeName":"first_name","KeyType":"HASH"},{"AttributeName":"last_name","KeyType":"RANGE"}],"Projection":{"ProjectionType":"ALL"},"ProvisionedThroughput":{"ReadCapacityUnits":5,"WriteCapacityUnits":5}}]' \
  --billing-mode PROVISIONED \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
```

## Running the Agent

### Development Mode

```bash
# Start the LangGraph development server
langgraph dev
```

The agent will be available at:
- **API**: http://127.0.0.1:2024
- **Studio UI**: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

### Using the Agent

Once running, you can interact via the Studio UI:

**Store a profile:**
```
Store my profile: John Doe, email john.doe@example.com, 
strengths: Learner, Achiever, Strategic, Futuristic, Analytical, ...
[include all 34 strengths in order]
```

**Retrieve a profile:**
```
What are John Doe's strengths?
```

## LangSmith Integration

The agent automatically integrates with [LangSmith](https://smith.langchain.com/) for tracing and debugging:

1. **Sign up** for a LangSmith account
2. **Add API key** to your `.env` file (see Setup step 2)
3. **View traces** in the LangSmith dashboard at https://smith.langchain.com/

LangSmith provides:
- Request/response traces for each agent interaction
- Performance metrics and latency tracking
- Debugging tools for tool calls and LLM responses
- Team collaboration features

## Running Tests

The project includes comprehensive unit tests.

```bash
# Run all tests
pytest

# Run unit tests with verbose output
pytest tests/unit_tests/ -v

# Run specific test files
pytest tests/unit_tests/test_db.py
pytest tests/unit_tests/test_tools.py

# Run with coverage report
pytest --cov=src/strengths_agent
```

**Test coverage:**
- `test_db.py` - DynamoDB client operations (10 tests)
- `test_tools.py` - Agent tool functions (8 tests)
- `test_configuration.py` - Context setup (3 tests)

For more details, see [TESTING_EXPLAINED.md](./TESTING_EXPLAINED.md) or [tests/README.md](./tests/README.md).

## Project Structure

```
src/strengths_agent/
├── graph.py        # Main agent graph with strengths_agent and db_tools nodes
├── tools.py        # DynamoDB tools (store_profile, get_profile)
├── db.py           # DynamoDB client wrapper
├── prompts.py      # System prompt with CliftonStrengths context
├── context.py      # Configuration and context management
└── state.py        # Agent state definitions

tests/
├── unit_tests/     # Unit tests (mocked AWS)
└── integration_tests/  # Integration tests
```

## Architecture

The agent follows a ReAct (Reasoning and Action) pattern:

1. **strengths_agent node**: LLM reasons about the user's request
2. **db_tools node**: Executes DynamoDB operations (store/retrieve profiles)
3. **Routing**: Agent decides when to use tools or respond directly

All interactions are traced in LangSmith when configured.

## Development Tips

- **Hot reload**: Code changes automatically apply when using `langgraph dev`
- **Edit history**: Use Studio UI to edit past states and rerun from checkpoints
- **Add tools**: Extend [tools.py](./src/strengths_agent/tools.py) with new functions
- **Modify prompts**: Update [prompts.py](./src/strengths_agent/prompts.py) to change agent behavior

## Troubleshooting

**AWS credentials expired:**
```bash
aws sso login --profile your-profile-name
```

**Module not found:**
```bash
pip install -e .
```

**Tests failing:**
```bash
# Install test dependencies
pip install pytest pytest-mock moto[dynamodb]
```
