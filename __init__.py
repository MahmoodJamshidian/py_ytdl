from typing import Literal
import requests
import re

class YTvideo:
    def __init__(self, url: str):
        self._session = requests.session()
        self._session.get("https://yt5s.io/en43")
        self.req_key = re.findall("X-Requested-Key\":\"([A-Za-z0-9]*)\"", self._session.get("https://yt5s.io/yt5s/js/app.min.js?v=3").text)[0]
        self._resp: dict = self._session.post("https://yt5s.io/api/ajaxSearch", data={"q": url, "vt": "home"}).json()
        if self._resp.get("mess", "").startswith("No data found") or self._resp.get("p", "non") != "convert":
            raise Exception("not found")
        
    @property
    def id(self):
        return self._resp.get("vid")
    
    @property
    def title(self):
        return self._resp.get("title")
    
    @property
    def channel(self):
        return self._resp.get("a")
    
    @property
    def links(self):
        return self._resp.get("links")
    
    def download_link(self, type: Literal["mp3", "mp4", "ogg", "3gp"], quality: str):
        if type in self.links:
            if quality in (self.links[type][i]['k'] for i in self.links[type].keys()):
                if not (s:=self._session.options("https://backend.svcenter.xyz/api/convert-by-45fc4be8916916ba3b8d61dd6e0d6994", headers={"Access-Control-Request-Headers": "x-requested-key", "Access-Control-Request-Method": "POST", "Origin": "https://yt5s.io"}).status_code) in range(200, 205):
                    raise Exception("server not ready")
                data = self._session.post("https://backend.svcenter.xyz/api/convert-by-45fc4be8916916ba3b8d61dd6e0d6994", headers={"X-Requested-Key": self.req_key}, data={"v_id": self._resp.get("vid"), "ftype": type, "fquality": quality, "token": self._resp.get("token"), "timeExpire": self._resp.get("timeExpires"), "client": "yt5s.io"}).json()
                if data["c_status"] != "ok":
                    raise Exception("error on generate url")
                return data['d_url']
            else:
                raise Exception("quality not found")
        else:
            raise Exception("type not found")
        
    def download(self, type: Literal["mp3", "mp4", "ogg", "3gp"], quality: str, filepath: str):
        with open(filepath, "wb") as f:
            with requests.get(self.download_link(type, quality), stream=True) as session:
                for buff in session.iter_content(1024):
                    f.write(buff)
