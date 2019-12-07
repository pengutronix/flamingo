from flamingo.core.data_model import Content


class FrontendController:
    def __init__(self, server):
        self.server = server

    def overlay_toggle(self):
        self.server.notify_sync('commands', {
            'method': 'ractive_fire',
            'event_name': 'toggle_overlay',
        })

    def overlay_show(self):
        self.server.notify_sync('commands', {
            'method': 'ractive_set',
            'keypath': 'settings.overlay.open',
            'value': True,
        })

    def overlay_hide(self):
        self.server.notify_sync('commands', {
            'method': 'ractive_set',
            'keypath': 'settings.overlay.open',
            'value': False,
        })

    def overlay_show_tab(self, tab):
        self.server.notify_sync('commands', {
            'method': 'ractive_set',
            'keypath': 'settings.overlay.tab',
            'value': tab,
        })

    def set_url(self, url):
        if isinstance(url, Content):
            url = url['url']

        self.server.notify_sync('commands', {
            'method': 'set_url',
            'url': url,
        })

    def reload(self):
        self.server.notify_sync('commands', {
            'method': 'reload',
        })
