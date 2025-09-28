# CI/CD Configuration for Streamlit Cloud Deployment
# This file documents the CI/CD pipeline setup

## Pipeline Overview

### 1. Quality Checks (`quality-checks.yml`)
- **Triggers**: Every push to main/develop, all PRs to main
- **Purpose**: Code quality, syntax validation, dependency testing
- **Includes**: Linting, formatting checks, import validation, Streamlit startup test

### 2. Streamlit Deployment (`streamlit-deploy.yml`)  
- **Triggers**: Push to main, manual workflow dispatch
- **Purpose**: Automated deployment to Streamlit Cloud
- **Features**: Pre-deployment checks, health monitoring, deployment notifications

### 3. Development Environment (`dev-environment.yml`)
- **Triggers**: Pull requests to main
- **Purpose**: Validate development setup, provide PR testing instructions
- **Features**: Environment validation, local testing instructions

## Deployment Flow

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Code Commit   │───▶│  Quality Checks  │───▶│    Deploy to    │
│   (to main)     │    │  - Lint & Test   │    │ Streamlit Cloud │
└─────────────────┘    │  - Validate App  │    └─────────────────┘
                       └──────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Health Check &  │
                       │  Notifications   │
                       └──────────────────┘
```

## Environment Variables (if needed)

For advanced configurations, you can set these in GitHub repository secrets:

- `STREAMLIT_SHARING_EMAIL`: Your Streamlit sharing email (optional)
- `DEPLOYMENT_WEBHOOK`: Custom webhook for notifications (optional)

## Manual Deployment Trigger

You can manually trigger deployment from GitHub Actions tab:
1. Go to Actions → Deploy to Streamlit Cloud
2. Click "Run workflow"
3. Select deployment environment
4. Click "Run workflow"

## Monitoring

- **GitHub Actions**: Monitor pipeline status in Actions tab
- **Streamlit Cloud**: Check deployment status at share.streamlit.io
- **Health Checks**: Automated health checks post-deployment

## App URLs

- **Production**: https://fnuashutosh-ai-job-tracker-assistant-main.streamlit.app
- **Dashboard**: https://share.streamlit.io

## Troubleshooting

Common issues and solutions:

1. **Dependency Issues**: Check requirements.txt format
2. **Python Version**: Ensure runtime.txt specifies python-3.11  
3. **Import Errors**: Verify all modules are properly structured
4. **Streamlit Startup**: Check app.py for syntax errors

## Pipeline Status Badges

Add these to your README.md:

```markdown
![Quality Checks](https://github.com/fnuAshutosh/ai-job-tracker-assistant/actions/workflows/quality-checks.yml/badge.svg)
![Streamlit Deploy](https://github.com/fnuAshutosh/ai-job-tracker-assistant/actions/workflows/streamlit-deploy.yml/badge.svg)
```