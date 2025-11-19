from kubernetes import client, config
from kubernetes.client.rest import ApiException
from app.config import Config
import yaml

class KubernetesDeployer:
    def __init__(self):
        self.configured = False
        try:
            # Try to load from default kubeconfig
            config.load_kube_config()
            self.apps_v1 = client.AppsV1Api()
            self.core_v1 = client.CoreV1Api()
            self.namespace = Config.K8S_NAMESPACE
            self.configured = True
            print("✅ Kubernetes configured successfully")
        except Exception as e:
            print(f"⚠️  WARNING: Kubernetes is not configured: {e}")
            print("   The app will run, but deployments will fail.")
            print("   See SETUP_GUIDE.md to enable Kubernetes.")
    
    def create_deployment(self, name, image, port=8080, replicas=2):
        """Create Kubernetes deployment"""
        
        if not self.configured:
            return False, "Kubernetes is not configured. Please enable Kubernetes in Docker Desktop."
        
        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=name),
            spec=client.V1DeploymentSpec(
                replicas=replicas,
                selector=client.V1LabelSelector(
                    match_labels={"app": name}
                ),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(
                        labels={"app": name}
                    ),
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name=name,
                                image=image,
                                ports=[client.V1ContainerPort(container_port=port)],
                                resources=client.V1ResourceRequirements(
                                    requests={"cpu": "100m", "memory": "128Mi"},
                                    limits={"cpu": "500m", "memory": "512Mi"}
                                )
                            )
                        ]
                    )
                )
            )
        )
        
        try:
            api_response = self.apps_v1.create_namespaced_deployment(
                namespace=self.namespace,
                body=deployment
            )
            print(f"Deployment created: {api_response.metadata.name}")
            return True, api_response.metadata.name
        except ApiException as e:
            if e.status == 409:
                # Deployment already exists, update it
                return self.update_deployment(name, image, port, replicas)
            print(f"Error creating deployment: {e}")
            return False, str(e)
    
    def update_deployment(self, name, image, port=8080, replicas=2):
        """Update existing Kubernetes deployment"""
        if not self.configured:
            return False, "Kubernetes is not configured."
        try:
            deployment = self.apps_v1.read_namespaced_deployment(
                name=name,
                namespace=self.namespace
            )
            
            deployment.spec.template.spec.containers[0].image = image
            
            api_response = self.apps_v1.patch_namespaced_deployment(
                name=name,
                namespace=self.namespace,
                body=deployment
            )
            print(f"Deployment updated: {api_response.metadata.name}")
            return True, api_response.metadata.name
        except ApiException as e:
            print(f"Error updating deployment: {e}")
            return False, str(e)
    
    def create_service(self, name, port=8080, target_port=8080, service_type="LoadBalancer"):
        """Create Kubernetes service"""
        
        if not self.configured:
            return False, "Kubernetes is not configured."
        
        service = client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=client.V1ObjectMeta(name=name),
            spec=client.V1ServiceSpec(
                selector={"app": name},
                ports=[client.V1ServicePort(
                    port=port,
                    target_port=target_port,
                    protocol="TCP"
                )],
                type=service_type
            )
        )
        
        try:
            api_response = self.core_v1.create_namespaced_service(
                namespace=self.namespace,
                body=service
            )
            print(f"Service created: {api_response.metadata.name}")
            return True, api_response.metadata.name
        except ApiException as e:
            if e.status == 409:
                print(f"Service {name} already exists")
                return True, name
            print(f"Error creating service: {e}")
            return False, str(e)
    
    def deploy_application(self, name, image, port=8080, replicas=2):
        """Complete deployment workflow"""
        # Create deployment
        success, message = self.create_deployment(name, image, port, replicas)
        if not success:
            return False, f"Deployment failed: {message}"
        
        # Create service
        success, message = self.create_service(name, port, port)
        if not success:
            return False, f"Service creation failed: {message}"
        
        return True, f"Application deployed successfully: {name}"
    
    def get_deployment_status(self, name):
        """Get deployment status"""
        if not self.configured:
            return None
        try:
            deployment = self.apps_v1.read_namespaced_deployment(
                name=name,
                namespace=self.namespace
            )
            return {
                'name': deployment.metadata.name,
                'replicas': deployment.spec.replicas,
                'available_replicas': deployment.status.available_replicas or 0,
                'ready_replicas': deployment.status.ready_replicas or 0
            }
        except ApiException as e:
            print(f"Error getting deployment status: {e}")
            return None
    
    def list_deployments(self):
        """List all deployments in namespace"""
        if not self.configured:
            return []
        try:
            deployments = self.apps_v1.list_namespaced_deployment(
                namespace=self.namespace
            )
            
            result = []
            for d in deployments.items:
                # Get service to find the port
                try:
                    service = self.core_v1.read_namespaced_service(
                        name=d.metadata.name,
                        namespace=self.namespace
                    )
                    # Get NodePort if available, otherwise use target port
                    if service.spec.type == 'NodePort' and service.spec.ports:
                        port = service.spec.ports[0].node_port
                    else:
                        port = service.spec.ports[0].port if service.spec.ports else 8000
                except:
                    port = 8000  # Default fallback
                
                result.append({
                    'name': d.metadata.name,
                    'replicas': d.spec.replicas,
                    'available_replicas': d.status.available_replicas or 0,
                    'image': d.spec.template.spec.containers[0].image,
                    'port': port
                })
            
            return result
        except ApiException as e:
            print(f"Error listing deployments: {e}")
            return []
    
    def delete_deployment(self, name):
        """Delete deployment and service"""
        if not self.configured:
            return False, "Kubernetes is not configured."
        try:
            # Delete deployment
            self.apps_v1.delete_namespaced_deployment(
                name=name,
                namespace=self.namespace
            )
            
            # Delete service
            self.core_v1.delete_namespaced_service(
                name=name,
                namespace=self.namespace
            )
            
            return True, f"Deleted deployment and service: {name}"
        except ApiException as e:
            print(f"Error deleting resources: {e}")
            return False, str(e)
