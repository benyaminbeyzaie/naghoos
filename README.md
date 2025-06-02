# Naghoos

A Discord bot that sends customized reminders to team members at scheduled times. The bot uses OpenAI's GPT model to generate creative and fun reminder messages specifically tailored for software engineering teams.

## Docker Image

This project includes a CI/CD pipeline that builds and pushes a private Docker image to GitHub Container Registry (ghcr.io) whenever changes are pushed to the main branch.

### Usage

1. Make sure your repository has the appropriate permissions to create packages:

   - Go to your repository settings
   - Navigate to "Actions" > "General"
   - Under "Workflow permissions", select "Read and write permissions"
   - Save changes

2. The Docker image will be available at:

   ```
   ghcr.io/YOUR_USERNAME/naghoos:latest
   ```

3. To pull the image locally (after authenticating):

   ```bash
   docker pull ghcr.io/YOUR_USERNAME/naghoos:latest
   ```

4. To run the container:
   ```bash
   docker run -d --name naghoos \
     -e DISCORD_TOKEN=your_token \
     -e OPENAI_API_KEY=your_key \
     -e OPENAI_BASE_URL=your_url \
     ghcr.io/YOUR_USERNAME/naghoos:latest
   ```
