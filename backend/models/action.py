from typing import Dict, Optional

class Action:
    def __init__(self, ActionID: int, APIID: int, Request: str, 
                 RequestTime: str, Response: str = "", ResponseTime: str = ""):
        self.ActionID = int(ActionID)
        self.APIID = int(APIID)
        self.Request = Request
        self.RequestTime = RequestTime
        self.Response = Response
        self.ResponseTime = ResponseTime
    
    def to_dict(self) -> Dict:
        return {
            'ActionID': self.ActionID,
            'APIID': self.APIID,
            'Request': self.Request,
            'RequestTime': self.RequestTime,
            'Response': self.Response,
            'ResponseTime': self.ResponseTime
        }
    
    def to_csv_dict(self) -> Dict:
        return {
            'ActionID': str(self.ActionID),
            'APIID': str(self.APIID),
            'Request': self.Request,
            'RequestTime': self.RequestTime,
            'Response': self.Response,
            'ResponseTime': self.ResponseTime
        }
    
    @staticmethod
    def from_csv_dict(data: Dict) -> 'Action':
        return Action(
            ActionID=data['ActionID'],
            APIID=data['APIID'],
            Request=data['Request'],
            RequestTime=data['RequestTime'],
            Response=data.get('Response', ''),
            ResponseTime=data.get('ResponseTime', '')
        )

class ThirdPartyAPI:
    def __init__(self, APIID: int, API_type: str, ProviderID: str, 
                 ProviderName: str, Key: str = "", URL: str = ""):
        self.APIID = int(APIID)
        self.API_type = API_type  # "LLM", "speech-to-text", "text-to-speech", "dictionary"
        self.ProviderID = ProviderID
        self.ProviderName = ProviderName
        self.Key = Key
        self.URL = URL
    
    def to_dict(self) -> Dict:
        return {
            'APIID': self.APIID,
            'API_type': self.API_type,
            'ProviderID': self.ProviderID,
            'ProviderName': self.ProviderName,
            'Key': self.Key,
            'URL': self.URL
        }
    
    def to_csv_dict(self) -> Dict:
        return {
            'APIID': str(self.APIID),
            'API_type': self.API_type,
            'ProviderID': self.ProviderID,
            'ProviderName': self.ProviderName,
            'Key': self.Key,
            'URL': self.URL
        }
    
    @staticmethod
    def from_csv_dict(data: Dict) -> 'ThirdPartyAPI':
        return ThirdPartyAPI(
            APIID=data['APIID'],
            API_type=data['API_type'],
            ProviderID=data['ProviderID'],
            ProviderName=data['ProviderName'],
            Key=data.get('Key', ''),
            URL=data.get('URL', '')
        )
