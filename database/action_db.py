import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.db_manager import CSVDatabase
from backend.models.action import Action, ThirdPartyAPI
from typing import Optional, List
from datetime import datetime
import json

class ActionDB:
    def __init__(self, db: CSVDatabase):
        self.db = db
        self.filename = "action.csv"
        self.fieldnames = ['ActionID', 'APIID', 'Request', 'RequestTime', 'Response', 'ResponseTime']
    
    def create_action(self, api_id: int, request: dict) -> Action:
        action_id = self.db.get_next_id(self.filename, 'ActionID')
        
        action = Action(
            ActionID=action_id,
            APIID=api_id,
            Request=json.dumps(request, ensure_ascii=False),
            RequestTime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            Response="",
            ResponseTime=""
        )
        
        self.db.append(self.filename, action.to_csv_dict(), self.fieldnames)
        return action
    
    def update_action_response(self, action_id: int, response: dict) -> bool:
        action = self.get_action(action_id)
        if not action:
            return False
        
        action.Response = json.dumps(response, ensure_ascii=False)
        action.ResponseTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return self.db.update_by_field(
            self.filename,
            'ActionID',
            str(action_id),
            action.to_csv_dict(),
            self.fieldnames
        )
    
    def get_action(self, action_id: int) -> Optional[Action]:
        data = self.db.find_by_field(self.filename, 'ActionID', str(action_id))
        if data:
            return Action.from_csv_dict(data)
        return None
    
    def get_actions_by_api(self, api_id: int) -> List[Action]:
        data = self.db.find_all_by_field(self.filename, 'APIID', str(api_id))
        return [Action.from_csv_dict(row) for row in data]

class ThirdPartyAPIDB:
    def __init__(self, db: CSVDatabase):
        self.db = db
        self.filename = "thirdpartyapi.csv"
        self.fieldnames = ['APIID', 'API_type', 'ProviderID', 'ProviderName', 'Key', 'URL']
    
    def get_api_by_id(self, api_id: int) -> Optional[ThirdPartyAPI]:
        data = self.db.find_by_field(self.filename, 'APIID', str(api_id))
        if data:
            return ThirdPartyAPI.from_csv_dict(data)
        return None
    
    def get_api_by_type(self, api_type: str) -> Optional[ThirdPartyAPI]:
        data = self.db.find_by_field(self.filename, 'API_type', api_type)
        if data:
            return ThirdPartyAPI.from_csv_dict(data)
        return None
    
    def update_api_key(self, api_id: int, key: str) -> bool:
        api = self.get_api_by_id(api_id)
        if not api:
            return False
        
        api.Key = key
        return self.db.update_by_field(
            self.filename,
            'APIID',
            str(api_id),
            api.to_csv_dict(),
            self.fieldnames
        )
    
    def get_all_apis(self) -> List[ThirdPartyAPI]:
        data = self.db.read(self.filename)
        return [ThirdPartyAPI.from_csv_dict(row) for row in data]
