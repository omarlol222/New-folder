# Manim Rendering Service Deployment Guide

This guide will help you deploy the Manim rendering service to a cloud platform.

## Option 1: Railway (Recommended - Easiest)

Railway offers a generous free tier and automatic Docker deployment.

### Steps:

1. **Create a Railway account**
   - Go to https://railway.app/
   - Sign up with GitHub

2. **Create a new project**
   - Click "New Project"
   - Select "Empty Project"

3. **Deploy from GitHub**
   - Push this `docker` folder to a GitHub repository
   - In Railway, click "Deploy from GitHub repo"
   - Select your repository
   - Railway will automatically detect the Dockerfile

4. **Configure the service**
   - Railway will auto-detect the Dockerfile in the `docker` folder
   - No additional configuration needed
   - The service will deploy automatically

5. **Get your service URL**
   - Once deployed, Railway will give you a public URL like:
     `https://your-service.railway.app`
   - Copy this URL

6. **Add the URL to Lovable**
   - Go to your Lovable project
   - In the chat, tell the AI to add a secret called `MANIM_SERVICE_URL`
   - Paste your Railway URL (e.g., `https://your-service.railway.app`)

### Testing the deployment:

```bash
curl https://your-service.railway.app/health
# Should return: {"status":"healthy","service":"manim-renderer"}
```

---

## Option 2: Google Cloud Run

Cloud Run offers automatic scaling and a generous free tier.

### Prerequisites:
- Google Cloud account
- `gcloud` CLI installed

### Steps:

1. **Build and push the Docker image**
   ```bash
   cd docker
   
   # Set your project ID
   export PROJECT_ID=your-gcp-project-id
   
   # Build the image
   docker build -t gcr.io/$PROJECT_ID/manim-renderer .
   
   # Push to Google Container Registry
   docker push gcr.io/$PROJECT_ID/manim-renderer
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy manim-renderer \
     --image gcr.io/$PROJECT_ID/manim-renderer \
     --platform managed \
     --region us-central1 \
     --memory 2Gi \
     --timeout 300 \
     --allow-unauthenticated
   ```

3. **Get the service URL**
   - Cloud Run will output a URL like: `https://manim-renderer-xxx.run.app`
   - Copy this URL

4. **Add to Lovable**
   - Add `MANIM_SERVICE_URL` secret with your Cloud Run URL

---

## Option 3: Render.com

Render offers a simple deployment process with a free tier.

### Steps:

1. **Create a Render account**
   - Go to https://render.com/
   - Sign up with GitHub

2. **Create a new Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect the Dockerfile

3. **Configure the service**
   - Name: `manim-renderer`
   - Region: Choose closest to your users
   - Instance Type: Start with "Free" (can upgrade later)
   - Render will automatically use the Dockerfile

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete

5. **Get your service URL**
   - Render will provide a URL like: `https://manim-renderer.onrender.com`
   - Copy this URL

6. **Add to Lovable**
   - Add `MANIM_SERVICE_URL` secret with your Render URL

---

## Testing Your Deployment

Once deployed, test with this curl command:

```bash
# Health check
curl https://your-service-url.com/health

# Test render (replace YOUR_URL)
curl -X POST https://your-service-url.com/render \
  -H "Content-Type: application/json" \
  -d '{
    "script": "from manim import *\n\nclass BasicScene(Scene):\n    def construct(self):\n        circle = Circle(radius=2, color=BLUE)\n        self.play(Create(circle))\n        self.wait(1)"
  }' \
  --output test.mp4
```

If successful, you'll get an `test.mp4` file!

---

## Troubleshooting

### Container memory issues
- Increase memory allocation (Railway: 2GB+, Cloud Run: 2Gi+, Render: upgrade tier)

### Timeout errors
- Rendering can take 30-120 seconds
- Ensure timeout settings are at least 300 seconds

### Manim rendering errors
- Check the service logs in your platform's dashboard
- Common issues: missing LaTeX packages, syntax errors in script

---

## Cost Estimates

- **Railway**: Free tier includes 500 hours/month, $5/month for hobby plan
- **Google Cloud Run**: Free tier: 2M requests/month, pay per use after
- **Render**: Free tier available, $7/month for starter plan

All platforms offer generous free tiers suitable for development and light usage.
