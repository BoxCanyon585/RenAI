# RenAI - Fast & Responsive AI Assistant

RenAI is a lightweight, fast AI assistant designed to run on your home network. It integrates seamlessly with Ollama for local LLM inference and provides a clean, responsive web interface for chatting with AI models.

(Upcoming itegration with uOS (https://github.com/syaomix/www-uos)

## Features

- **Fast & Responsive**: Built with FastAPI and async operations for optimal performance
- **Ollama Integration**: Works with local Ollama models for privacy and speed
- **Streaming Responses**: Real-time token streaming for immediate feedback
- **Clean Web Interface**: Modern, responsive UI with dark mode support
- **Easy Deployment**: Docker support for simple home network setup
- **Multiple Models**: Switch between different Ollama models on the fly

## Architecture

- **Backend**: FastAPI (Python 3.11+) with async operations
- **Frontend**: Vanilla JavaScript with Server-Sent Events (SSE)
- **LLM Provider**: Ollama for local model inference
- **Deployment**: Docker & docker-compose

## Prerequisites

Before running RenAI, ensure you have the following installed:

1. **Ollama**: Download and install from [ollama.ai](https://ollama.ai)
2. **Python 3.11+** (for native installation) OR **Docker** (for containerized deployment)
3. **At least one Ollama model**: Pull a model using `ollama pull llama2`

## Quick Start

### Option 1: Docker (Recommended)

1. **Install and start Ollama** on your host machine:
   ```bash
   # Install Ollama from https://ollama.ai

   # Pull a model (e.g., llama2)
   ollama pull llama2

   # Verify Ollama is running (should be automatic)
   curl http://localhost:11434/api/tags
   ```

2. **Clone and run RenAI**:
   ```bash
   git clone <repository-url>
   cd RenAI

   # Optional: Copy and customize environment variables
   cp .env.example .env

   # Build and start with Docker Compose
   docker-compose up -d
   ```

3. **Access the interface**:
   - Open your browser to `http://localhost:8000`
   - Or from another device on your network: `http://<your-server-ip>:8000`

### Option 2: Native Python Installation

1. **Install and start Ollama** (same as above)

2. **Set up RenAI**:
   ```bash
   git clone <repository-url>
   cd RenAI

   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Optional: Configure environment
   cp .env.example .env
   ```

3. **Run the application**:
   ```bash
   # From the project root
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

   # Or with auto-reload for development
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Access the interface**:
   - Open `http://localhost:8000`

## Configuration

You can configure RenAI using environment variables. Create a `.env` file in the project root:

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama2

# Model Parameters
MAX_TOKENS=2048
TEMPERATURE=0.7
TOP_P=0.9

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Frontend
FRONTEND_PATH=./frontend
```

### Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_BASE_URL` | Ollama API endpoint | `http://localhost:11434` |
| `DEFAULT_MODEL` | Default model to use | `llama2` |
| `MAX_TOKENS` | Maximum tokens to generate | `2048` |
| `TEMPERATURE` | Sampling temperature (0-1) | `0.7` |
| `TOP_P` | Top-p sampling parameter | `0.9` |
| `HOST` | Server bind address | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `DEBUG` | Enable debug mode | `false` |
| `FRONTEND_PATH` | Path to frontend files | `./frontend` |

## Usage

1. **Select a Model**: Choose from available Ollama models in the dropdown
2. **Type Your Message**: Enter your message in the text area
3. **Send**: Click the send button or press Enter
4. **Watch the Response**: The AI response streams in real-time
5. **Continue Chatting**: Keep the conversation going!

### Keyboard Shortcuts

- **Enter**: Send message
- **Shift + Enter**: New line in message

## Project Structure

```
RenAI/
├── backend/                 # FastAPI backend
│   ├── main.py             # Application entry point
│   ├── config.py           # Configuration settings
│   ├── models.py           # Pydantic models
│   ├── services/
│   │   └── ollama_service.py  # Ollama integration
│   ├── routers/
│   │   ├── chat.py         # Chat endpoints
│   │   └── health.py       # Health check
│   └── utils/
│       └── streaming.py    # SSE utilities
├── frontend/               # Web interface
│   ├── index.html         # Main HTML
│   └── static/
│       ├── css/
│       │   └── styles.css # Styling
│       └── js/
│           ├── app.js     # Application logic
│           └── chat.js    # Chat manager
├── tests/                 # Test files
├── .env.example          # Environment template
├── .gitignore           # Git ignore rules
├── docker-compose.yml   # Docker Compose config
├── Dockerfile          # Docker image definition
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## API Documentation

Once the application is running, you can access:

- **Interactive API Docs**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`

### Main Endpoints

- `GET /health` - Health check endpoint
- `GET /api/models` - List available Ollama models
- `POST /api/chat/stream` - Streaming chat endpoint

## Troubleshooting

### Ollama Not Connected

**Error**: "Warning: Ollama is not connected"

**Solutions**:
1. Ensure Ollama is installed and running: `ollama list`
2. Check if Ollama is accessible: `curl http://localhost:11434/api/tags`
3. Verify the `OLLAMA_BASE_URL` in your configuration

### No Models Available

**Error**: "No models available"

**Solutions**:
1. Pull a model: `ollama pull llama2`
2. Verify models are installed: `ollama list`
3. Restart the RenAI application

### Docker Connection Issues (Linux)

On Linux, `host.docker.internal` may not work. Update `docker-compose.yml`:

```yaml
environment:
  - OLLAMA_BASE_URL=http://172.17.0.1:11434  # Docker bridge IP
```

Or use your host machine's IP address:

```yaml
environment:
  - OLLAMA_BASE_URL=http://192.168.1.x:11434
```

### Port Already in Use

**Error**: "Address already in use"

**Solutions**:
1. Stop other services using port 8000
2. Change the port in `.env` or `docker-compose.yml`

## Development

### Running in Development Mode

```bash
# With auto-reload
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

## Network Access

### Local Network Access

By default, RenAI is accessible to all devices on your local network:

1. Find your server's IP address:
   ```bash
   # On macOS/Linux
   ifconfig | grep "inet "

   # On Windows
   ipconfig
   ```

2. Access from other devices: `http://<server-ip>:8000`

### Setting a Static IP (Optional)

For consistent access, configure a static IP for your server in your router's DHCP settings, or add a DNS entry (e.g., `renai.local`).

## Security Notes

- **Current Version**: No authentication (suitable for trusted home networks only)
- **Network Isolation**: Ensure your firewall blocks external access to port 8000
- **Future Enhancement**: Authentication can be added for internet exposure

## Performance

- **First Token Latency**: <500ms (hardware dependent)
- **UI Load Time**: <100ms
- **Memory Footprint**: <100MB backend
- **Concurrent Users**: Supports multiple simultaneous conversations

## Future Roadmap

- [ ] Conversation history persistence (SQLite)
- [ ] Multi-conversation support (chat sessions)
- [ ] Custom system prompts
- [ ] File upload for RAG context
- [ ] Authentication system
- [ ] Dark/Light theme toggle
- [ ] Export conversations as Markdown
- [ ] Progressive Web App (PWA) support
- [ ] Voice input integration

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

[Add your license here]

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [Ollama](https://ollama.ai)
- Inspired by the need for fast, private, local AI assistants

---

**Enjoy chatting with RenAI!** 🚀
