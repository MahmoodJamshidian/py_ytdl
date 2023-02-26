from bs4 import BeautifulSoup
import requests
import re

class YTvideo:
    def __init__(self, url: str):
        self._session = requests.session()
        try:
            bs = BeautifulSoup((req:=self._session.get(f"https://10downloader.com/download?v={url}&lang=en&type=video", timeout=5, allow_redirects=False)).text, "html.parser")
            if req.status_code == 302:
                raise RuntimeError
        except requests.exceptions.ReadTimeout or RuntimeError:
            raise Exception("not found")
        self._title = bs.find("span", {"class": "title"}).text
        self._duration = bs.find("div", {"class": "duration"})
        self._duration.find("span").clear()
        self._duration = self._duration.text.replace("\n", "").strip()
        self._thumbnail = bs.find("div", {"class": "info"}).find("img").attrs['src']
        _vids, _auds = [i.find("tbody") for i in bs.find_all("table", {"class": "downloadsTable"})[:2]]
        self._links = {"vid": [], "aud": []}
        for _vid in _vids.find_all("tr"):
            _quality, _type, _size = [i.text for i in _vid.find_all("td")[:3]]
            _link = _vid.find_all("td")[3].find("a").attrs['href']
            self._links['vid'].append({'quality': _quality, "type": _type, "size": _size, "link": _link})
        for _aud in _auds.find_all("tr"):
            _quality, _type, _size = [i.text for i in _aud.find_all("td")[:3]]
            _link = _aud.find_all("td")[3].find("a").attrs['href']
            self._links['aud'].append({'quality': _quality, "type": _type, "size": _size, "link": _link})
        self._id = re.findall("vi_webp/([a-zA-Z0-9]*)/", self._thumbnail)[0]
        
    @property
    def id(self):
        return self._id
    
    @property
    def title(self):
        return self._title
    
    @property
    def channel(self):
        raise NotImplementedError
    
    @property
    def links(self):
        return self._links
    
    @staticmethod
    def download(link: str, filepath: str):
        with open(filepath, "wb") as f:
            with requests.get(link, stream=True) as session:
                for buff in session.iter_content(1024):
                    f.write(buff)
