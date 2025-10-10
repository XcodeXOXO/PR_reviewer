# API Reference — AI PR Reviewer

## Base URL
`http://127.0.0.1:8000` (Local)  
`https://<your-ngrok-id>.ngrok-free.app` (Public Demo)

---

### **POST** `/review`
Run an AI-powered pull request review.

#### Request Body
```json
{
  "provider": "github",
  "repo": "pallets/flask",
  "pr_number": 3154,
  "max_findings": 5
}
