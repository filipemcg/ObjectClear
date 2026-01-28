from functools import lru_cache
from typing import Optional
import urllib.parse
import requests
import json
from requests import Response
import os

class CMDB:
    def __init__(self, url: str) -> None:
        self.url = url
        self.headers = {
        'Content-Type': 'application/json'
        }

    @lru_cache(maxsize=128)
    def get_sites(self) -> Response:
        url = f"{self.url}/api/sites"
        response = requests.get(url, headers=self.headers)
        return response

    def get_advertisments(self) -> Response:
        url = f"{self.url}/api/advertisements"
        response = requests.get(url, headers=self.headers)
        return response

    def update_advertisement(self, id: int, data: dict) -> Response:
        url = f"{self.url}/api/advertisements/{str(id)}"
        response = requests.put(url, headers=self.headers, data=json.dumps(data))
        return response

    def get_advertisment_by_username(self, username) -> Response:
        url = f"{self.url}/api/advertisements/search?username={username}"
        response = requests.get(url, headers=self.headers)
        return response

    def get_advertisment_by_section(self, section: str) -> Response:
        url = f"{self.url}/api/advertisements/search?section={section}"
        response = requests.get(url, headers=self.headers)
        return response

    def get_blacklisted_advertisments(self) -> Response:
        url = f"{self.url}/api/advertisements/search?blacklist=true"
        response = requests.get(url, headers=self.headers)
        return response

    def get_contact(self, id: int) -> Response:
        url = f"{self.url}/api/contacts/{str(id)}"
        response = requests.get(url, headers=self.headers)
        return response

    def get_contact_list(self, page_num: int, page_size: int) -> Response:
        url = f"{self.url}/api/contacts"
        params = {'pageNum': page_num, 'pageSize': page_size}
        response = requests.get(url, headers=self.headers, params=params)
        return response

    def get_advertisement_list(self) -> Response:
        url = f"{self.url}/api/advertisements"
        response = requests.get(url, headers=self.headers)
        return response

    def get_location_list(self) -> Response:
        url = f"{self.url}/api/locations"
        response = requests.get(url, headers=self.headers)
        return response

    def get_contact_by_phone(self, phone: str):
        phone = urllib.parse.quote(phone)
        url = f"{self.url}/api/contacts/search?phone={phone}"
        response = requests.get(url, headers=self.headers)
        return response

    def update_contact(self, id: int, contact: dict) -> Response:
        url = f"{self.url}/api/contacts/{str(id)}"
        response = requests.put(url, headers=self.headers, data=json.dumps(contact))
        return response

    def create_contact(self, contact: dict) -> Response:
        url = f"{self.url}/api/contacts"
        response = requests.post(url, headers=self.headers, data=json.dumps(contact))
        return response

    def create_content(self, content: dict) -> Response:
        url = f"{self.url}/api/content"
        response = requests.post(url, headers=self.headers, data=json.dumps(content))
        return response

    def get_verified_profiles(self, domain: Optional[str] = None) -> Response:
        url = f"{self.url}/api/profiles/verified"
        if domain:
            params = {'domain': domain}
            response = requests.get(url, params=params)
        else:
            response = requests.get(url)
        return response

    def get_content_score_greater_than(self, score: int):
        url = f"{self.url}/api/content/score?gt={str(score)}"
        response = requests.get(url, headers=self.headers)
        return response

    def get_profile_by_url(self, url: str):
        url = urllib.parse.quote(url)
        url = f"{self.url}/api/profiles/search?url={url}"
        response = requests.get(url, headers=self.headers)
        return response

    def get_profile_by_phone(self, phone: str):
        phone = urllib.parse.quote(phone)
        url = f"{self.url}/api/profiles/search?phone={phone}"
        response = requests.get(url, headers=self.headers)
        return response

    def get_profiles_score_greater_than(self, score: float):
        url = f"{self.url}/api/profiles/score?gt={str(score)}"
        response = requests.get(url, headers=self.headers)
        return response

    def get_profiles_list(self, page_num: int, page_size: int) -> Response:
        url = f"{self.url}/api/profiles"
        params = {'pageNum': page_num, 'pageSize': page_size}
        response = requests.get(url, headers=self.headers, params=params)
        return response

    def update_profile(self, id: int, profile: dict):
        url = f"{self.url}/api/profiles/{str(id)}"
        response = requests.put(url, headers=self.headers, data=json.dumps(profile))
        return response

    def set_profiles_inactive(self) -> Response:
        url = f"{self.url}/api/profiles/inactive"
        response = requests.put(url, headers=self.headers)
        return response

    def create_profile(self, profile: dict) -> Response:
        url = f"{self.url}/api/profiles"
        response = requests.post(url, headers=self.headers, data=json.dumps(profile))
        return response

    def update_profile_info(self, id: int, profile_info: dict):
        url = f"{self.url}/api/profile-info/{str(id)}"
        response = requests.put(url, headers=self.headers, data=json.dumps(profile_info))
        return response

    def create_profile_info(self, profile_info: dict) -> Response:
        url = f"{self.url}/api/profile-info"
        response = requests.post(url, headers=self.headers, data=json.dumps(profile_info))
        return response

    def get_content_by_id(self, id: str):
        url = f"{self.url}/api/content/{id}"
        response = requests.get(url, headers=self.headers)
        return response

    def get_content_by_phone(self, phone: str):
        phone = urllib.parse.quote(phone)
        url = f"{self.url}/api/content/search?phone={phone}"
        response = requests.get(url, headers=self.headers)
        return response

    def get_s3_content_by_url(self, url: str):
        url = urllib.parse.quote(url)
        url = f"{self.url}/api/s3/search?url={url}"
        response = requests.get(url, headers=self.headers)
        return response

    def create_s3_content(self, s3_content: dict) -> Response:
        """
        {
            "content_id": fields.Integer(required=True),
            "step": fields.String,
            "s3_uri": fields.String
        }
        """
        url = f"{self.url}/api/s3"
        response = requests.post(url, headers=self.headers, data=json.dumps(s3_content))
        return response