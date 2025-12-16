# Perplexity Trading Bot - Isolated Service

A completely isolated FastAPI service for Perplexity-powered trading analysis.

## 🎯 Architecture Overview

This service runs independently on **port 8001** and provides:
- **Isolated Environment**: Standalone service
- **Fresh FastAPI Instance**: Clean, simple middleware stack
- **Direct Perplexity Integration**: Enhanced prompts for trading analysis
- **Comprehensive Error Handling**: Proper HTTP responses and logging
- **Image Analysis Support**: Chart upload and analysis capabilities

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Perplexity API key

### 1. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Perplexity API key
PERPLEXITY_API_KEY=your_api_key_here
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the Service
```bash
# Method 1: Direct Python
python main.py

# Method 2: Using batch file (Windows)
../../start-perplexity-bot.bat

# Method 3: Using PowerShell (Windows)
../../Start-PerplexityBot.ps1
```

### 4. Verify Service
```bash
# Health check
curl http://localhost:8001/health

# Test chat endpoint
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Analyze Bitcoin price action"}'
```

## 📡 API Endpoints

### Health Check
```http
GET /health
GET /api/health
```

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "timestamp": "2024-01-01T12:00:00",
  "perplexity_api_configured": true
}
```

### Chat Analysis
```http
POST /api/chat
```

**Request:**
```json
{
  "message": "Analyze Bitcoin price action",
  "image_data": "base64_encoded_image_optional",
  "conversation_history": [
    {"role": "user", "content": "Previous message"},
    {"role": "assistant", "content": "Previous response"}
  ],
  "model": "sonar-pro",
  "temperature": 0.2,
  "max_tokens": 4000
}
```

**Response:**
```json
{
  "success": true,
  "message": "Comprehensive analysis...",
  "citations": [
    {
      "title": "Source Title",
      "url": "https://example.com",
      "snippet": "Relevant excerpt..."
    }
  ],
  "related_questions": [
    "What are the key support levels?",
    "How does volume confirm this analysis?"
  ],
  "model_used": "sonar-pro",
  "tokens_used": 1250,
  "processing_time": 3.45,
  "error": null
}
```

### Available Models
```http
GET /api/models
```

**Response:**
```json
{
  "models": [
    {
      "id": "sonar-pro",
      "name": "Sonar Pro",
      "description": "Advanced model for comprehensive analysis",
      "max_tokens": 4000
    }
  ],
  "default_model": "sonar-pro"
}
```

## 🧠 Enhanced Prompt System

The service automatically enhances user prompts based on query type detection:

### Query Types
1. **Chart Analysis**: Technical analysis with institutional focus
2. **Position Check**: Risk assessment and management
3. **Market Research**: Comprehensive market intelligence
4. **Price Check**: Current market analysis

### Prompt Enhancement Features
- **Institutional Language**: Uses professional trading terminology
- **Specific Requirements**: Requests actionable insights with price levels
- **Context Awareness**: Adapts based on image presence
- **Risk Focus**: Emphasizes risk-reward ratios and scenarios

## 🖼️ Image Analysis

Upload chart images for comprehensive technical analysis:

```javascript
// Frontend example
const formData = new FormData();
formData.append('image', file);
formData.append('message', 'Analyze this chart');

const response = await fetch('/api/chat', {
  method: 'POST',
  body: formData
});
```

## 🔧 Configuration

### Environment Variables
```bash
# API Configuration
PERPLEXITY_API_KEY=your_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8001
DEBUG=false
LOG_LEVEL=INFO

# Model Configuration
DEFAULT_MODEL=sonar-pro
MAX_TOKENS=4000
TEMPERATURE=0.2

# Rate Limiting
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW=60
```

### CORS Configuration
The service allows requests from:
- `http://localhost:3000` (Frontend dev)
- `http://localhost:8000` (OpenWeb UI)
- `http://127.0.0.1:3000`
- `http://127.0.0.1:8000`

## 📊 Logging

Logs are written to both console and file:
- **File**: `logs/app.log`
- **Format**: `timestamp - logger - level - message`
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Log Examples
```
2024-01-01 12:00:00 - perplexity_service - INFO - Calling Perplexity API with model: sonar-pro
2024-01-01 12:00:03 - perplexity_service - INFO - Perplexity API call successful in 3.45s
2024-01-01 12:00:03 - main - INFO - Request: POST /api/chat
2024-01-01 12:00:03 - main - INFO - Response: 200 - 3.456s
```

## 🐳 Docker Deployment

### Build and Run
```bash
# Build image
docker build -t perplexity-trading-bot .

# Run container
docker run -d \
  --name perplexity-bot \
  -p 8001:8001 \
  -e PERPLEXITY_API_KEY=your_key \
  perplexity-trading-bot
```

### Docker Compose
```bash
# Start with existing services
docker-compose -f docker-compose.perplexity.yml up -d

# View logs
docker-compose -f docker-compose.perplexity.yml logs perplexity-bot

# Stop services
docker-compose -f docker-compose.perplexity.yml down
```

## 🔍 Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check Python version
python --version  # Should be 3.8+

# Check dependencies
pip list | grep fastapi

# Check port availability
netstat -an | findstr :8001
```

#### API Key Issues
```bash
# Verify API key is set
echo $PERPLEXITY_API_KEY

# Test API key manually
curl -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  https://api.perplexity.ai/chat/completions
```

#### CORS Errors
- Ensure frontend is running on allowed origins
- Check browser console for specific CORS messages
- Verify `ALLOWED_ORIGINS` in config.py

#### Connection Refused
```bash
# Check if service is running
curl http://localhost:8001/health

# Check logs
tail -f logs/app.log

# Verify port binding
netstat -tlnp | grep :8001
```

### Debug Mode
```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Start service
python main.py
```

## 📈 Performance

### Typical Response Times
- **Text Analysis**: 2-4 seconds
- **Image Analysis**: 4-8 seconds
- **Health Check**: <100ms

### Resource Usage
- **Memory**: ~50-100MB
- **CPU**: Low (spikes during API calls)
- **Network**: Depends on Perplexity API usage

### Rate Limiting
- **Default**: 60 requests per minute
- **Configurable**: Via environment variables
- **Per-endpoint**: Can be customized

## 🔐 Security

### API Key Protection
- Never commit API keys to version control
- Use environment variables or secure vaults
- Rotate keys regularly

### Network Security
- Service runs on localhost by default
- Configure firewall rules for production
- Use HTTPS in production environments

### Input Validation
- All inputs validated with Pydantic models
- File upload size limits enforced
- Malicious content filtering

## 🚀 Production Deployment

### Recommended Setup
1. **Reverse Proxy**: Use nginx or similar
2. **Process Manager**: Use systemd or supervisor
3. **Monitoring**: Health checks and alerting
4. **Logging**: Centralized log aggregation
5. **Scaling**: Multiple instances behind load balancer

### Environment Configuration
```bash
# Production settings
DEBUG=false
LOG_LEVEL=WARNING
HOST=0.0.0.0
PORT=8001

# Security
ALLOWED_ORIGINS=https://yourdomain.com
```

### Systemd Service (Linux)
```ini
[Unit]
Description=Perplexity Trading Bot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/perplexity_bot
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📚 Integration Examples

### Frontend Integration
```javascript
// API client usage
import { perplexityAPI } from '$lib/apis/perplexity';

// Send message
const response = await perplexityAPI.sendMessage({
  message: "Analyze Bitcoin",
  model: "sonar-pro"
});

// Upload image
const response = await perplexityAPI.uploadImageForAnalysis(
  imageFile, 
  "Analyze this chart"
);
```

### Backend Integration
```python
# Direct service usage
from services.perplexity_service import perplexity_service

result = await perplexity_service.process_message(
    message="Analyze market conditions",
    model="sonar-pro"
)
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Make changes and test thoroughly
4. Commit: `git commit -m "Add new feature"`
5. Push: `git push origin feature/new-feature`
6. Create Pull Request

## 📄 License

This project is part of the TradeBerg ecosystem and follows the same licensing terms.

## 🆘 Support

For issues and questions:
1. Check this README
2. Review logs in `logs/app.log`
3. Test with health endpoint
4. Create GitHub issue with details

---

**Service Status**: ✅ Production Ready  
**Last Updated**: November 2024  
**Version**: 1.0.0
