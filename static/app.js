// Global state
let repos = [];
let deployments = [];

// DOM Elements
const reposContainer = document.getElementById('repos-container');
const reposLoading = document.getElementById('repos-loading');
const deploymentsContainer = document.getElementById('deployments-container');
const deploymentsLoading = document.getElementById('deployments-loading');
const deployModal = document.getElementById('deploy-modal');
const repoSearch = document.getElementById('repo-search');

// Tab switching
document.querySelectorAll('.menu-item').forEach(item => {
    item.addEventListener('click', () => {
        const tabName = item.dataset.tab;
        
        // Update active menu item
        document.querySelectorAll('.menu-item').forEach(mi => mi.classList.remove('active'));
        item.classList.add('active');
        
        // Update active tab content
        document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
        document.getElementById(`${tabName}-tab`).classList.add('active');
        
        // Load data for the selected tab
        if (tabName === 'repositories') {
            loadRepositories();
        } else if (tabName === 'deployments') {
            loadDeployments();
        }
    });
});

// Load repositories
async function loadRepositories() {
    if (reposLoading) reposLoading.style.display = 'block';
    if (reposContainer) reposContainer.innerHTML = '';
    
    try {
        const response = await fetch('/api/repos');
        const data = await response.json();
        
        if (data.repos) {
            repos = data.repos;
            displayRepositories(repos);
        } else {
            showError('Failed to load repositories');
        }
    } catch (error) {
        console.error('Error loading repositories:', error);
        showError('Failed to load repositories');
    } finally {
        if (reposLoading) reposLoading.style.display = 'none';
    }
}

// Display repositories
function displayRepositories(reposToDisplay) {
    if (!reposContainer) return;
    
    reposContainer.innerHTML = '';
    
    if (reposToDisplay.length === 0) {
        reposContainer.innerHTML = '<p style="text-align:center; color: var(--text-secondary);">No repositories found</p>';
        return;
    }
    
    reposToDisplay.forEach(repo => {
        const repoCard = document.createElement('div');
        repoCard.className = 'repo-card';
        repoCard.innerHTML = `
            <h3>${repo.name}</h3>
            <p>${repo.description || 'No description'}</p>
            <div class="repo-meta">
                ${repo.language ? `<span class="repo-language">${repo.language}</span>` : ''}
                <span>Updated: ${new Date(repo.updated_at).toLocaleDateString()}</span>
            </div>
            <button class="btn btn-primary" onclick="deployRepository('${repo.clone_url}', '${repo.name}')">
                🚀 Deploy
            </button>
        `;
        reposContainer.appendChild(repoCard);
    });
}

// Search repositories
if (repoSearch) {
    repoSearch.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const filtered = repos.filter(repo => 
            repo.name.toLowerCase().includes(searchTerm) ||
            (repo.description && repo.description.toLowerCase().includes(searchTerm))
        );
        displayRepositories(filtered);
    });
}

// Deploy repository
async function deployRepository(repoUrl, repoName) {
    deployModal.classList.add('active');
    
    // Reset stages
    document.querySelectorAll('.deploy-stage').forEach(stage => {
        stage.classList.remove('success', 'error');
        stage.querySelector('.stage-icon').textContent = '⏳';
    });
    
    document.getElementById('deploy-result').classList.add('hidden');
    
    try {
        const response = await fetch('/api/deploy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                repo_url: repoUrl,
                repo_name: repoName
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Mark all stages as success
            document.querySelectorAll('.deploy-stage').forEach(stage => {
                stage.classList.add('success');
                stage.querySelector('.stage-icon').textContent = '✅';
            });
            
            showDeployResult(true, `Successfully deployed ${repoName}!<br>Image: ${data.image}<br>Deployment: ${data.deployment}`);
        } else {
            // Mark error stage
            const errorStage = data.stage || 'unknown';
            document.getElementById(`stage-${errorStage.split('_')[0]}`).classList.add('error');
            
            showDeployResult(false, `Deployment failed: ${data.error}`);
        }
    } catch (error) {
        console.error('Deployment error:', error);
        showDeployResult(false, `Deployment failed: ${error.message}`);
    }
}

// Show deploy result
function showDeployResult(success, message) {
    const resultDiv = document.getElementById('deploy-result');
    resultDiv.classList.remove('hidden');
    resultDiv.className = success ? 'alert alert-success' : 'alert alert-error';
    resultDiv.innerHTML = message;
}

// Load deployments
async function loadDeployments() {
    if (deploymentsLoading) deploymentsLoading.style.display = 'block';
    if (deploymentsContainer) deploymentsContainer.innerHTML = '';
    
    try {
        const response = await fetch('/api/deployments');
        const data = await response.json();
        
        if (data.deployments) {
            deployments = data.deployments;
            displayDeployments(deployments);
        } else {
            showError('Failed to load deployments');
        }
    } catch (error) {
        console.error('Error loading deployments:', error);
        showError('Failed to load deployments');
    } finally {
        if (deploymentsLoading) deploymentsLoading.style.display = 'none';
    }
}

// Display deployments
function displayDeployments(deploymentsToDisplay) {
    if (!deploymentsContainer) return;
    
    deploymentsContainer.innerHTML = '';
    
    if (deploymentsToDisplay.length === 0) {
        deploymentsContainer.innerHTML = '<p style="text-align:center; color: var(--text-secondary);">No deployments found</p>';
        return;
    }
    
    deploymentsToDisplay.forEach(deployment => {
        const deploymentCard = document.createElement('div');
        deploymentCard.className = 'deployment-card';
        
        const isHealthy = deployment.available_replicas === deployment.replicas;
        const statusColor = isHealthy ? 'var(--success-color)' : 'var(--warning-color)';
        
        // Construct the app URL
        const appUrl = `http://localhost:${deployment.port}`;
        
        deploymentCard.innerHTML = `
            <div class="deployment-header">
                <h3>${deployment.name}</h3>
                <span style="color: ${statusColor};">
                    ${isHealthy ? '✅ Healthy' : '⚠️ Unhealthy'}
                </span>
            </div>
            <div class="deployment-status">
                <div class="status-item">
                    <span class="status-label">Replicas</span>
                    <span class="status-value">${deployment.available_replicas}/${deployment.replicas}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Image</span>
                    <span class="status-value" style="font-size: 0.9rem;">${deployment.image}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Port</span>
                    <span class="status-value">${deployment.port}</span>
                </div>
            </div>
            <div class="deployment-actions">
                <a href="${appUrl}" target="_blank" class="btn btn-primary" style="text-decoration: none;">
                    🌐 View App
                </a>
                <button class="btn btn-secondary" onclick="viewDeploymentDetails('${deployment.name}')">
                    📊 Details
                </button>
                <button class="btn btn-danger" onclick="deleteDeployment('${deployment.name}')">
                    🗑️ Delete
                </button>
            </div>
        `;
        deploymentsContainer.appendChild(deploymentCard);
    });
}

// View deployment details
async function viewDeploymentDetails(name) {
    try {
        const response = await fetch(`/api/deployment/${name}`);
        const data = await response.json();
        
        if (data.status) {
            alert(`Deployment: ${name}\nReplicas: ${data.status.replicas}\nReady: ${data.status.ready_replicas}\nAvailable: ${data.status.available_replicas}`);
        }
    } catch (error) {
        console.error('Error getting deployment details:', error);
    }
}

// Delete deployment
async function deleteDeployment(name) {
    if (!confirm(`Are you sure you want to delete deployment "${name}"?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/deployment/${name}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Deployment deleted successfully');
            loadDeployments();
        } else {
            alert(`Failed to delete deployment: ${data.error}`);
        }
    } catch (error) {
        console.error('Error deleting deployment:', error);
        alert('Failed to delete deployment');
    }
}

// Refresh buttons
document.getElementById('refresh-repos')?.addEventListener('click', loadRepositories);
document.getElementById('refresh-deployments')?.addEventListener('click', loadDeployments);

// Close modal
document.querySelector('.close')?.addEventListener('click', () => {
    deployModal.classList.remove('active');
});

// Close modal on outside click
window.addEventListener('click', (e) => {
    if (e.target === deployModal) {
        deployModal.classList.remove('active');
    }
});

// Show error
function showError(message) {
    alert(message);
}

// Initial load
if (document.getElementById('repositories-tab')) {
    loadRepositories();
}
