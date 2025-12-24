# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in Nexus Financial Analyst, please report it by creating a private security advisory on GitHub or by contacting the maintainers directly. Please do not open public issues for security vulnerabilities.

## Security Best Practices

### API Keys and Secrets Management

1. **Never commit sensitive data**: Always use environment variables for API keys and secrets
2. **Use .env files**: Store your API keys in a `.env` file (already in `.gitignore`)
3. **Rotate exposed keys**: If you accidentally commit API keys, rotate them immediately
4. **Use .env.example**: Use `backend/.env.example` as a template

### Environment Variables

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `TAVILY_API_KEY`: Your Tavily API key (for web search)
- `LLM_NAME`: The LLM model name (e.g., gpt-4o-mini)
- `LLM_BASE_URL`: The LLM API base URL

### CORS Configuration

The backend is configured with CORS middleware to only allow requests from:
- `http://localhost:5173` (Vite default)
- `http://localhost:3000` (alternative dev server)

For production deployment, update the `allow_origins` list in `backend/main.py` with your production domain.

### Input Validation

- Message length is limited to 10,000 characters to prevent abuse
- All inputs are validated before processing
- Error messages are generic to avoid information disclosure

### Security Headers

The API responses include the following security headers:
- `X-Content-Type-Options: nosniff` - Prevents MIME type sniffing
- `X-Frame-Options: DENY` - Prevents clickjacking attacks
- `X-XSS-Protection: 1; mode=block` - Enables XSS filtering

### Logging

- Logging is configured to avoid logging sensitive data
- Only operation types and ticker symbols are logged, not full query content
- API keys are never logged

### Rate Limiting

Consider implementing rate limiting in production to prevent abuse:
- Use middleware like `slowapi` or `fastapi-limiter`
- Set reasonable limits per IP address or user session

## Security Checklist for Deployment

- [ ] Rotate all API keys before production deployment
- [ ] Update CORS origins to match production domain
- [ ] Enable HTTPS/TLS for all connections
- [ ] Implement rate limiting
- [ ] Set up monitoring and alerting
- [ ] Review and update dependencies regularly
- [ ] Use a reverse proxy (nginx, Caddy) for additional security
- [ ] Implement proper authentication if needed
- [ ] Set up firewall rules
- [ ] Enable audit logging

## Dependencies

Keep dependencies up to date to address security vulnerabilities:

```bash
# Backend
pip install --upgrade -r requirements.txt

# Frontend
npm update
npm audit fix
```

## Compliance

This application handles financial data. Ensure compliance with:
- Data protection regulations (GDPR, CCPA, etc.)
- Financial regulations in your jurisdiction
- Terms of service for third-party APIs (OpenAI, Tavily, yfinance)

## Disclaimer

This application is provided for educational and informational purposes only. It is not financial advice. Users are responsible for:
- Securing their own API keys
- Complying with applicable laws and regulations
- Ensuring proper data handling and privacy practices
- Making their own investment decisions

## Updates

This security policy will be updated as the project evolves. Check back regularly for updates.
