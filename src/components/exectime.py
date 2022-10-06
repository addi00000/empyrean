import time

from discord import Embed, SyncWebhook


class exec_time(object):
    def __init__(self):
        self._start = time.time()
        self._stop = None

    def stop(self):
        self._stop = time.time()

    def get_time(self):
        return round(self._stop - self._start, 2)

    def send(self, webhook: str):
        webhook = SyncWebhook.from_url(webhook)
        embed = Embed(title="Execution Time",
                      description=f"Execution time: {self.get_time()} seconds", color=0x000000)
        webhook.send(embed=embed, username="Empyrean",
                     avatar_url="https://i.imgur.com/HjzfjfR.png")
