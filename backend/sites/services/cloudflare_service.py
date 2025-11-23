import requests
from django.conf import settings

class CloudflareService:
    BASE_URL = "https://api.cloudflare.com/client/v4"

    def __init__(self, token):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def create_zone(self, domain):
        """
        Create a new zone (site) in Cloudflare.
        """
        url = f"{self.BASE_URL}/zones"
        data = {
            "name": domain,
            "account": {"id": self._get_account_id()}, # We might need to fetch account ID first or let user provide it? 
            # Actually, usually token is scoped to an account or we can just try creating it. 
            # If token has access to multiple accounts, we might need to specify.
            # For now, let's try without account if possible, or fetch the first available one.
            "jump_start": True
        }
        
        # If we need account ID, we should probably fetch it from the token's access
        if not data['account']['id']:
             account_id = self._get_first_account_id()
             if account_id:
                 data['account']['id'] = account_id
             else:
                 # Fallback or error
                 pass

        response = requests.post(url, headers=self.headers, json=data)
        return response.json()

    def get_ns_records(self, zone_id):
        """
        Get Nameserver records for a zone.
        """
        url = f"{self.BASE_URL}/zones/{zone_id}/dns_records?type=NS"
        response = requests.get(url, headers=self.headers)
        return response.json()
        
    def get_zone_details(self, zone_id):
        url = f"{self.BASE_URL}/zones/{zone_id}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def create_page_rule(self, zone_id, rule_data):
        """
        Create a page rule (e.g., for forwarding).
        """
        url = f"{self.BASE_URL}/zones/{zone_id}/pagerules"
        response = requests.post(url, headers=self.headers, json=rule_data)
        return response.json()

    def _get_account_id(self):
        """
        Try to get account ID from token verification endpoint first, 
        then fall back to listing accounts.
        """
        # Verify token endpoint often returns the user/account context
        url = f"{self.BASE_URL}/user/tokens/verify"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                # Sometimes the verification response doesn't directly give account ID, 
                # but let's check if we can get it from a standard "accounts" list if not here.
                pass 
        except Exception:
            pass
            
        return self._get_first_account_id()

    def _get_first_account_id(self):
        """
        Helper to get the first account ID available to this token.
        """
        url = f"{self.BASE_URL}/accounts"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('result'):
                    return data['result'][0]['id']
        except Exception as e:
            print(f"Error fetching Cloudflare accounts: {e}")
            
        return None

    def deploy_to_pages(self, project_name, zip_path):
        """
        Deploy a ZIP file to Cloudflare Pages using Direct Upload.
        """
        account_id = self._get_account_id() or self._get_first_account_id()
        if not account_id:
            raise Exception("Could not retrieve Cloudflare Account ID")

        # 1. Ensure Project Exists
        self._ensure_pages_project(account_id, project_name)

        # 2. Upload Deployment
        url = f"{self.BASE_URL}/accounts/{account_id}/pages/projects/{project_name}/deployments"
        
        try:
            with open(zip_path, 'rb') as f:
                files = {
                    'file': ('site.zip', f, 'application/zip')
                }
                # Note: requests automatically sets Content-Type to multipart/form-data when 'files' is passed
                # We need to ensure we don't override it with application/json in headers
                upload_headers = self.headers.copy()
                upload_headers.pop('Content-Type', None)
                
                response = requests.post(url, headers=upload_headers, files=files)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise Exception(f"Deployment failed: {response.text}")
                    
        except Exception as e:
            print(f"Error deploying to Cloudflare: {e}")
            raise e

    def _ensure_pages_project(self, account_id, project_name):
        """
        Ensure the Pages project exists.
        """
        url = f"{self.BASE_URL}/accounts/{account_id}/pages/projects"
        
        # Check if exists
        get_url = f"{url}/{project_name}"
        response = requests.get(get_url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
            
        # Create if not
        data = {
            "name": project_name,
            "production_branch": "main",
            # "source": {"type": "direct_upload"} # Not strictly needed for direct upload projects usually, but good practice
        }
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()
