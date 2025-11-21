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
        # Placeholder: In a real scenario, we might store the account ID with the token 
        # or fetch it. For now, let's return None and handle it in _get_first_account_id
        return None

    def _get_first_account_id(self):
        """
        Helper to get the first account ID available to this token.
        """
        url = f"{self.BASE_URL}/accounts"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('result'):
                return data['result'][0]['id']
        return None
