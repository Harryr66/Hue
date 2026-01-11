# Set Up GitHub Actions for Vercel Deployment

## Quick Setup

### 1. Get Vercel Tokens

Run this command to get your Vercel credentials:

```bash
cd /Users/harry/Desktop/HUE/ui-nextjs
vercel link
```

This will create a `.vercel` folder. Check it for your IDs:

```bash
cat ui-nextjs/.vercel/project.json
```

You'll see:
- `orgId` (this is `VERCEL_ORG_ID`)
- `projectId` (this is `VERCEL_PROJECT_ID`)

### 2. Get Vercel Token

1. Go to: https://vercel.com/account/tokens
2. Create a new token
3. Copy the token (you'll only see it once!)

### 3. Add Secrets to GitHub

1. Go to your GitHub repository: https://github.com/Harryr66/Hue
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add these three secrets:
   - Name: `VERCEL_TOKEN` → Value: (your token from step 2)
   - Name: `VERCEL_ORG_ID` → Value: (your org ID from step 1)
   - Name: `VERCEL_PROJECT_ID` → Value: (your project ID from step 1)

### 4. Commit the Workflow

The GitHub Actions workflow file is already created at `.github/workflows/deploy-vercel.yml`.

Commit and push it:

```bash
cd /Users/harry/Desktop/HUE
git add .github/workflows/deploy-vercel.yml
git commit -m "Add GitHub Actions for Vercel deployment"
git push origin main
```

### 5. Test It

After pushing, GitHub Actions will automatically:
- Trigger on pushes to `main` branch
- Only when files in `ui-nextjs/` change
- Deploy to Vercel production

Check status at: https://github.com/Harryr66/Hue/actions

## How It Works

- ✅ **Automatic:** Deploys on every push to `main`
- ✅ **Smart:** Only triggers when `ui-nextjs/` files change
- ✅ **Production:** Deploys directly to production (`--prod`)
- ✅ **No Python builds:** Only builds Next.js from `ui-nextjs/`

## Manual Deployment (Alternative)

If you don't want to set up GitHub Actions, just deploy manually:

```bash
cd /Users/harry/Desktop/HUE/ui-nextjs
vercel --prod
```

## Which Should You Use?

- **GitHub Actions:** Automated, deploy on every push
- **Manual CLI:** Simple, deploy when you want

You can use both! GitHub Actions for automated deploys, or `vercel --prod` for manual deployments.

