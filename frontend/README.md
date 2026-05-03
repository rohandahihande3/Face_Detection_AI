# Face Detection AI Frontend

Lightweight React app served by Nginx.

## Run Locally

```bash
npm install
REACT_APP_API_BASE_URL=http://localhost:5000 npm start
```

## Build

```bash
npm run build
```

## Camera Access

Browsers only allow webcam access on secure origins:

- `http://localhost`
- `https://your-domain.com`

Camera mode will not work on a plain LAN or EC2 IP such as `http://192.168.1.48` or `http://EC2_PUBLIC_IP`. Image upload still works there.

For EC2 camera support, put the app behind HTTPS with a domain and TLS certificate, then open `https://your-domain.com`.
