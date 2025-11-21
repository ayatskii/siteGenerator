from celery import shared_task
import time

@shared_task
def generate_site_task(site_id):
    """
    Placeholder task for site generation.
    """
    print(f"Starting generation for site {site_id}...")
    # Simulate work
    time.sleep(5)
    print(f"Finished generation for site {site_id}.")
    return f"Site {site_id} generated."

@shared_task
def deploy_site_task(deployment_id):
    """
    Placeholder task for site deployment.
    """
    print(f"Starting deployment {deployment_id}...")
    # Simulate work
    time.sleep(5)
    print(f"Finished deployment {deployment_id}.")
    return f"Deployment {deployment_id} completed."
