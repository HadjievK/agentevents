# Agent Events Website

Official documentation site for Agent Events - [agentevents.io](https://agentevents.io)

## Overview

This is a static website showcasing the Agent Events specification - a simple, open format for giving AI agents scheduled workflows and event-driven automation.

## Local Development

Simply open `index.html` in your browser:

```bash
# macOS
open index.html

# Windows
start index.html

# Linux
xdg-open index.html
```

Or use a simple HTTP server:

```bash
# Python 3
python -m http.server 8000

# Node.js
npx serve
```

Then visit `http://localhost:8000`

## Deploy to Cloudflare Pages

### Option 1: GitHub Integration (Recommended)

1. **Create GitHub repository:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/HadjievK/agentevents.git
   git push -u origin main
   ```

2. **Connect to Cloudflare Pages:**
   - Log in to [Cloudflare Dashboard](https://dash.cloudflare.com)
   - Go to **Pages** → **Create a project**
   - Select **Connect to Git**
   - Choose your repository: `HadjievK/agentevents`
   - Build settings:
     - **Build command:** (leave empty - static site)
     - **Build output directory:** `/`
   - Click **Save and Deploy**

3. **Configure custom domain:**
   - In your Cloudflare Pages project, go to **Custom domains**
   - Click **Set up a custom domain**
   - Enter `agentevents.io`
   - Cloudflare will automatically configure DNS

### Option 2: Direct Upload

1. **Install Wrangler CLI:**
   ```bash
   npm install -g wrangler
   ```

2. **Login to Cloudflare:**
   ```bash
   wrangler login
   ```

3. **Deploy:**
   ```bash
   wrangler pages deploy . --project-name=agentevents
   ```

4. **Configure custom domain:**
   - Go to your Pages project in Cloudflare Dashboard
   - Add custom domain `agentevents.io`

### Option 3: Manual Upload

1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Go to **Pages** → **Create a project** → **Upload assets**
3. Name your project: `agentevents`
4. Drag and drop the site files (`index.html`, `style.css`)
5. Click **Deploy site**
6. Configure custom domain in project settings

## Custom Domain Setup

Once deployed, configure your domain:

1. **In Cloudflare Pages:**
   - Go to your project → **Custom domains**
   - Add `agentevents.io` and `www.agentevents.io`

2. **DNS will be automatically configured:**
   - `agentevents.io` → CNAME to `agentevents.pages.dev`
   - `www.agentevents.io` → CNAME to `agentevents.pages.dev`

3. **SSL certificate is automatic** - Cloudflare provisions it within minutes

## File Structure

```
agentevents/
├── index.html          # Main page
├── style.css           # Stylesheet
└── README.md           # This file
```

## Making Updates

### Via GitHub (if using GitHub integration):

```bash
# Make changes to index.html or style.css
git add .
git commit -m "Update content"
git push

# Cloudflare Pages will auto-deploy in ~1 minute
```

### Via Direct Upload:

```bash
wrangler pages deploy . --project-name=agentevents
```

## Performance

- **Build time:** Instant (static site)
- **Global CDN:** Served from 300+ Cloudflare edge locations
- **SSL:** Automatic HTTPS with Cloudflare Universal SSL
- **Cost:** Free on Cloudflare Pages Free tier

## Links

- Live site: [agentevents.io](https://agentevents.io)
- Specification: [GitHub - HadjievK/agentevents](https://github.com/HadjievK/agentevents)

## Inspiration

This site is inspired by [agentskills.io](https://agentskills.io) and follows similar design principles for clarity and professionalism.

## License

MIT License - see individual repositories for details.
