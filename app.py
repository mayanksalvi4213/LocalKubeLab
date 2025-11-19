from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from app.config import Config
from app.github_auth import GitHubAuth
from app.docker_builder import DockerBuilder
from app.k8s_deployer import KubernetesDeployer
import os

app = Flask(__name__)
app.config.from_object(Config)

# Initialize services
docker_builder = DockerBuilder()
k8s_deployer = KubernetesDeployer()

@app.route('/')
def index():
    """Home page"""
    if 'access_token' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login')
def login():
    """Redirect to GitHub OAuth"""
    auth_url = GitHubAuth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    """GitHub OAuth callback"""
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'No authorization code received'}), 400
    
    # Exchange code for access token
    access_token = GitHubAuth.get_access_token(code)
    if not access_token:
        return jsonify({'error': 'Failed to get access token'}), 400
    
    # Get user info
    user_info = GitHubAuth.get_user_info(access_token)
    if not user_info:
        return jsonify({'error': 'Failed to get user info'}), 400
    
    # Store in session
    session['access_token'] = access_token
    session['user'] = {
        'login': user_info.get('login'),
        'name': user_info.get('name'),
        'avatar_url': user_info.get('avatar_url')
    }
    
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard"""
    if 'access_token' not in session:
        return redirect(url_for('index'))
    
    return render_template('dashboard.html', user=session.get('user'))

@app.route('/api/repos')
def get_repos():
    """Get user's GitHub repositories"""
    if 'access_token' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    repos = GitHubAuth.get_user_repos(session['access_token'])
    
    # Format repo data
    formatted_repos = [{
        'name': repo.get('name'),
        'full_name': repo.get('full_name'),
        'description': repo.get('description'),
        'clone_url': repo.get('clone_url'),
        'language': repo.get('language'),
        'updated_at': repo.get('updated_at')
    } for repo in repos]
    
    return jsonify({'repos': formatted_repos})

@app.route('/api/deploy', methods=['POST'])
def deploy():
    """Deploy selected repository"""
    if 'access_token' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    repo_url = data.get('repo_url')
    repo_name = data.get('repo_name')
    
    if not repo_url or not repo_name:
        return jsonify({'error': 'Repository URL and name required'}), 400
    
    # Sanitize repo name for Docker/K8s
    safe_name = repo_name.lower().replace('_', '-').replace('.', '-')
    
    try:
        # Step 1: Build and push Docker image
        success, result = docker_builder.build_and_push(
            repo_url=repo_url,
            image_name=safe_name,
            tag='latest'
        )
        
        if not success:
            return jsonify({
                'success': False,
                'stage': 'docker_build',
                'error': result
            }), 500
        
        image_name = result
        
        # Step 2: Detect port based on project type (stored during build)
        port = getattr(docker_builder, 'last_detected_port', 8000)
        
        # Step 2: Deploy to Kubernetes
        success, result = k8s_deployer.deploy_application(
            name=safe_name,
            image=image_name,
            port=port,
            replicas=2
        )
        
        if not success:
            return jsonify({
                'success': False,
                'stage': 'k8s_deploy',
                'error': result
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Deployment successful',
            'image': image_name,
            'deployment': safe_name,
            'port': port
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/deployments')
def get_deployments():
    """Get all deployments"""
    if 'access_token' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        deployments = k8s_deployer.list_deployments()
        return jsonify({'deployments': deployments})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/deployment/<name>')
def get_deployment_status(name):
    """Get specific deployment status"""
    if 'access_token' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        status = k8s_deployer.get_deployment_status(name)
        if status:
            return jsonify({'status': status})
        return jsonify({'error': 'Deployment not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/deployment/<name>', methods=['DELETE'])
def delete_deployment(name):
    """Delete deployment"""
    if 'access_token' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Delete from Kubernetes
        success, message = k8s_deployer.delete_deployment(name)
        if success:
            # Also delete Docker image to clean up
            try:
                import subprocess
                image_name = f"{Config.DOCKERHUB_USERNAME}/{name}:latest"
                
                # Remove Docker image
                result = subprocess.run(
                    ['docker', 'rmi', image_name],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                
                if result.returncode == 0:
                    message += f" and cleaned up Docker image"
                else:
                    message += f" (image cleanup skipped - may be in use)"
            except Exception as img_error:
                print(f"Could not remove Docker image: {img_error}")
            
            return jsonify({'success': True, 'message': message})
        return jsonify({'success': False, 'error': message}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
