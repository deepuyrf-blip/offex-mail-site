OFFEX AUDIO — CLOUDFLARE + HUGGING FACE SECURE PROXY

Files:
- index.html
- _worker.js

Cloudflare variables/secrets:
1) HF_TOKEN
   Type: Secret / Encrypt
   Value: your Hugging Face token (starts with hf_)

2) HF_SPACE_URL
   Type: Plain text variable
   Value: https://hydui-ytvideo.hf.space

How it works:
Browser -> /hf -> Cloudflare Worker -> Hugging Face Space

The browser never receives HF_TOKEN. HTTP requests and Gradio WebSocket
connections are both proxied by the Worker, and the token is attached only
server-side.

IMPORTANT:
- Do NOT put the HF token inside index.html.
- Do NOT put the HF token in localStorage or frontend JavaScript.
- After adding/changing variables, redeploy the Pages project.
