import os
import subprocess
import tempfile
import shutil
from git import Repo
from app.config import Config

class DockerBuilder:
    def __init__(self):
        self.dockerhub_username = Config.DOCKERHUB_USERNAME
        self.dockerhub_password = Config.DOCKERHUB_PASSWORD
    
    def clone_repository(self, repo_url, temp_dir):
        """Clone GitHub repository to temporary directory"""
        try:
            Repo.clone_from(repo_url, temp_dir)
            return True
        except Exception as e:
            print(f"Error cloning repository: {e}")
            return False
    
    def detect_project_type(self, temp_dir):
        """Detect what type of project this is and return (type, port)"""
        files = os.listdir(temp_dir)
        
        # Check for Node.js
        if 'package.json' in files:
            return 'nodejs', 3000
        
        # Check for Python
        if 'requirements.txt' in files or any(f.endswith('.py') for f in files):
            return 'python', 8000
        
        # Check for Go
        if 'go.mod' in files or any(f.endswith('.go') for f in files):
            return 'go', 8000
        
        # Check for static HTML/JS
        if any(f.endswith('.html') for f in files):
            return 'static', 80
        
        # Default to static
        return 'static', 80
    
    def create_dockerfile(self, temp_dir, language='python'):
        """Create a basic Dockerfile if one doesn't exist"""
        dockerfile_path = os.path.join(temp_dir, 'Dockerfile')
        
        if os.path.exists(dockerfile_path):
            print("Found existing Dockerfile")
            return True
        
        # Auto-detect project type
        project_type, port = self.detect_project_type(temp_dir)
        self.last_detected_port = port  # Store for later use
        print(f"Detected project type: {project_type} (port: {port})")
        
        if project_type == 'static':
            # Static HTML/JS/CSS - use Nginx
            dockerfile_content = """FROM nginx:alpine

COPY . /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
"""
        
        elif project_type == 'nodejs':
            # Node.js app
            dockerfile_content = """FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
"""
        
        elif project_type == 'go':
            # Go app
            dockerfile_content = """FROM golang:1.21-alpine AS builder

WORKDIR /app

COPY go.* ./
RUN go mod download

COPY . .
RUN go build -o main .

FROM alpine:latest
WORKDIR /app
COPY --from=builder /app/main .

EXPOSE 8000

CMD ["./main"]
"""
        
        else:  # python
            # Check if requirements.txt exists
            has_requirements = os.path.exists(os.path.join(temp_dir, 'requirements.txt'))
            
            # Detect main Python file
            main_file = 'app.py'
            possible_mains = ['app.py', 'main.py', 'server.py', 'run.py']
            for filename in possible_mains:
                if os.path.exists(os.path.join(temp_dir, filename)):
                    main_file = filename
                    break
            else:
                # Find any .py file
                for file in os.listdir(temp_dir):
                    if file.endswith('.py') and not file.startswith('__'):
                        main_file = file
                        break
            
            # Python Dockerfile
            if has_requirements:
                dockerfile_content = f"""FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "{main_file}"]
"""
            else:
                dockerfile_content = f"""FROM python:3.9-slim

WORKDIR /app

COPY . .

EXPOSE 8000

CMD ["python", "{main_file}"]
"""
        
        try:
            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile_content.strip())
            print(f"Created Dockerfile for {project_type} project")
            return True
        except Exception as e:
            print(f"Error creating Dockerfile: {e}")
            return False
    
    def build_image(self, temp_dir, image_name, tag='latest'):
        """Build Docker image"""
        try:
            full_image_name = f"{self.dockerhub_username}/{image_name}:{tag}"
            
            result = subprocess.run(
                ['docker', 'build', '-t', full_image_name, '.'],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0:
                print(f"Successfully built image: {full_image_name}")
                return full_image_name
            else:
                print(f"Error building image: {result.stderr}")
            return None
        except Exception as e:
            print(f"Error building image: {e}")
            return None
    
    def login_dockerhub(self):
        """Login to Docker Hub"""
        try:
            result = subprocess.run(
                ['docker', 'login', '-u', self.dockerhub_username, '-p', self.dockerhub_password],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Error logging into Docker Hub: {e}")
            return False
    
    def push_image(self, image_name):
        """Push Docker image to Docker Hub"""
        try:
            result = subprocess.run(
                ['docker', 'push', image_name],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0:
                print(f"Successfully pushed image: {image_name}")
                return True
            else:
                print(f"Error pushing image: {result.stderr}")
                return False
        except Exception as e:
            print(f"Error pushing image: {e}")
            return False
    
    def build_and_push(self, repo_url, image_name, tag='latest'):
        """Complete workflow: clone, build, and push"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Clone repository
            if not self.clone_repository(repo_url, temp_dir):
                return False, "Failed to clone repository"
            
            # Create Dockerfile if needed
            self.create_dockerfile(temp_dir)
            
            # Build image
            full_image_name = self.build_image(temp_dir, image_name, tag)
            if not full_image_name:
                return False, "Failed to build Docker image"
            
            # Login to Docker Hub
            if not self.login_dockerhub():
                return False, "Failed to login to Docker Hub"
            
            # Push image
            if not self.push_image(full_image_name):
                return False, "Failed to push image to Docker Hub"
            
            return True, full_image_name
        
        finally:
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)
