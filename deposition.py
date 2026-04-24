import json
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# Initialize environment
load_dotenv()

class ScientificDeposition:
    """
    Handles professional-grade deposition of structural predictions
    to global scientific databases (Zenodo, ModelArchive).
    """
    
    def __init__(self):
        self.zenodo_url = "https://zenodo.org/api/deposit/depositions"
        self.zenodo_token = os.getenv("ZENODO_TOKEN")
        
    def create_zenodo_draft(self, sequence: str, pdb_content: str, metadata: dict):
        """
        Creates a draft deposition on Zenodo.
        If no token is found, generates a local manifest for manual upload.
        """
        if not self.zenodo_token:
            return self._generate_manual_manifest(sequence, pdb_content, metadata, "Zenodo")
            
        try:
            # 1. Create Deposition
            headers = {"Content-Type": "application/json"}
            params = {'access_token': self.zenodo_token}
            
            data = {
                'metadata': {
                    'title': f"NRC Structural Prediction: {metadata.get('hash', 'unidentified')}",
                    'upload_type': 'dataset',
                    'description': f"Automated structural prediction for sequence: {sequence[:100]}... using NRC {metadata.get('folding_mode', 'Engine')}.",
                    'creators': [{'name': 'Nexus Resonance Codex Protocol', 'affiliation': 'NRC Open Research'}],
                    'access_right': 'open',
                    'license': 'CC-BY-NC-SA-4.0'
                }
            }
            
            r = requests.post(self.zenodo_url, params=params, data=json.dumps(data), headers=headers)
            if r.status_code != 201:
                raise Exception(f"Zenodo Init Failed: {r.json().get('message', 'Unknown Error')}")
                
            deposition_id = r.json()['id']
            bucket_url = r.json()['links']['bucket']
            
            # 2. Upload PDB File
            filename = f"nrc_prediction_{metadata.get('hash', 'result')}.pdb"
            requests.put(f"{bucket_url}/{filename}", data=pdb_content, params=params)
            
            return {
                "status": "SUCCESS",
                "id": deposition_id,
                "url": f"https://zenodo.org/deposit/{deposition_id}",
                "message": f"Deposition draft created successfully. DOI pending review."
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "message": str(e),
                "fallback": self._generate_manual_manifest(sequence, pdb_content, metadata, "Zenodo")
            }

    def _generate_manual_manifest(self, sequence: str, pdb_content: str, metadata: dict, target: str):
        """Generates a JSON manifest for manual scientific submission."""
        manifest = {
            "deposition_target": target,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "title": f"NRC Structural Prediction: {metadata.get('hash', 'unidentified')}",
                "creators": [{"name": "Nexus Resonance Codex Protocol"}],
                "description": f"Automated structural prediction for sequence: {sequence[:50]}...",
                "access_right": "open",
                "license": "CC-BY-NC-SA-4.0"
            },
            "system_info": {
                "engine": metadata.get("folding_mode", "NRC"),
                "stability": metadata.get("ttt_stability", 7.0)
            }
        }
        return manifest

# Singleton
depositor = ScientificDeposition()
