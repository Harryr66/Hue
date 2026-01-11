# Manual Deployment to Vercel

## Deploy to Production

Whenever you want to deploy your changes:

```bash
cd /Users/harry/Desktop/HUE/ui-nextjs
vercel --prod
```

That's it! Your site will be deployed to: https://hue-gold.vercel.app

## Typical Workflow

1. **Make changes to your code**

2. **Commit and push to GitHub** (optional, for version control):
   ```bash
   cd /Users/harry/Desktop/HUE
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```

3. **Deploy to Vercel**:
   ```bash
   cd ui-nextjs
   vercel --prod
   ```

## Quick Commands

**Deploy to production:**
```bash
cd ui-nextjs && vercel --prod
```

**Preview deployment (test before production):**
```bash
cd ui-nextjs && vercel
```

**Redeploy last deployment:**
```bash
cd ui-nextjs && vercel --prod --force
```

## Environment Variables

Make sure environment variables are set in Vercel Dashboard:
- Go to: https://vercel.com/harrys-projects-4097042e/hue/settings/environment-variables
- Add/update variables as needed

Changes to environment variables require a new deployment to take effect.

