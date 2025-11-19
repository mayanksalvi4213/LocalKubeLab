import requests
from flask import session, redirect, url_for, request
from app.config import Config

class GitHubAuth:
    AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
    TOKEN_URL = 'https://github.com/login/oauth/access_token'
    API_URL = 'https://api.github.com'
    
    @staticmethod
    def get_authorize_url():
        """Generate GitHub OAuth authorization URL"""
        params = {
            'client_id': Config.GITHUB_CLIENT_ID,
            'redirect_uri': Config.GITHUB_REDIRECT_URI,
            'scope': 'repo read:user'
        }
        return f"{GitHubAuth.AUTHORIZE_URL}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    
    @staticmethod
    def get_access_token(code):
        """Exchange authorization code for access token"""
        data = {
            'client_id': Config.GITHUB_CLIENT_ID,
            'client_secret': Config.GITHUB_CLIENT_SECRET,
            'code': code,
            'redirect_uri': Config.GITHUB_REDIRECT_URI
        }
        headers = {'Accept': 'application/json'}
        
        response = requests.post(GitHubAuth.TOKEN_URL, data=data, headers=headers)
        if response.status_code == 200:
            return response.json().get('access_token')
        return None
    
    @staticmethod
    def get_user_info(access_token):
        """Get authenticated user information"""
        headers = {
            'Authorization': f'token {access_token}',
            'Accept': 'application/json'
        }
        response = requests.get(f"{GitHubAuth.API_URL}/user", headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    
    @staticmethod
    def get_user_repos(access_token):
        """Get user's repositories"""
        headers = {
            'Authorization': f'token {access_token}',
            'Accept': 'application/json'
        }
        repos = []
        page = 1
        
        while True:
            response = requests.get(
                f"{GitHubAuth.API_URL}/user/repos",
                headers=headers,
                params={'page': page, 'per_page': 100, 'sort': 'updated'}
            )
            if response.status_code != 200:
                break
            
            data = response.json()
            if not data:
                break
                
            repos.extend(data)
            page += 1
            
            if len(data) < 100:
                break
        
        return repos
    
    @staticmethod
    def get_repo_details(access_token, owner, repo):
        """Get specific repository details"""
        headers = {
            'Authorization': f'token {access_token}',
            'Accept': 'application/json'
        }
        response = requests.get(
            f"{GitHubAuth.API_URL}/repos/{owner}/{repo}",
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        return None
