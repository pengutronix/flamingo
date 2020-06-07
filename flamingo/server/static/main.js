// Cookies --------------------------------------------------------------------
function set_cookie(name, value) {
    return Cookies.set(name, value);
}

function get_cookie(name, default_value) {
    var value = Cookies.get(name);

    if(value !== undefined) {
        return JSON.parse(value);
    }

    return default_value;
}

// Ractive / Settings ---------------------------------------------------------
Ractive.DEBUG = false;

var _default_settings = {
    _version: 1,
    overlay: {
        open: false,
        tab: 'meta-data',
    },
    log: {
        logger: {},
        level: {
            debug: false,
            info: false,
            warning: true,
            error: true,
            critical: true,
        },
    },
    keyboard_shortcuts: true,
    show_full_content_repr: false,
    show_internal_meta_data: false,
    pulsing_errors: true,
};

function get_default_settings() {
    return JSON.parse(JSON.stringify(_default_settings));
}

function generate_settings() {
    var default_settings = get_default_settings();
    var settings = get_cookie('flamingo_settings', default_settings);

    if(settings._version != default_settings._version) {
        set_cookie('flamingo_settings', default_settings);

        return default_settings;
    }

    return settings;
}

var ractive = Ractive({
    target: '#ractive',
    template: '#main',
    data: {
        server_options: {},
        connected: true,
        dots: [],
        messages: [],
        settings: generate_settings(),
        content: {},
        plugin_options_html: '',
        log: {
            logger: [],
            records: [],
        },
    },
    computed: {
        tabs: function() {
            var tabs = [
                'meta-data',
                'template-context',
                'project-settings',
                'log',
                'settings',
            ];

            if(this.get('plugin_options_html')) {
                tabs.unshift('plugin-options');
            }

            return tabs;
        },
        tab: function() {
            var selected_tab = this.get('settings.overlay.tab');
            var tabs = this.get('tabs');
            var tab_exists = tabs.indexOf(selected_tab) >= 0;

            if(!tab_exists) {
                selected_tab = tabs[0];
            }

            return selected_tab;
        },
    },
});

ractive.observe('settings', function () {
    set_cookie('flamingo_settings', ractive.get('settings'));
});

ractive.on('reset_settings', function() {
    ractive.set('settings', get_default_settings());

    show_message('<span class="important">Settings reseted</span> ' +
                 'Please reload the browser tab');
});

// server options -------------------------------------------------------------
ractive.on('toggle_directory_index', function() {
    rpc.call('toggle_option', 'directory_index');
});

ractive.on('toggle_directory_listing', function() {
    rpc.call('toggle_option', 'directory_listing');
});

// RPC ------------------------------------------------------------------------
var rpc_protocol = 'ws://';

if(window.location.protocol == 'https:') {
    rpc_protocol = 'wss://';
}

var rpc = new RPC(rpc_protocol + window.location.host + '/_flamingo/rpc/');
rpc.DEBUG = false;

ractive.on('clear_log', function(event) {
    rpc.call('clear_log', undefined, function(data) {
        ractive.set('log.records', []);
    });
});

ractive.on('start_shell', function(event) {
    rpc.call('start_shell');
});

// iframe handling ------------------------------------------------------------
var iframe = document.querySelector('iframe#content');
var iframe_initial_setup = false;

function iframe_update_meta_data() {
    var settings = ractive.get('settings');

    if(!rpc || !rpc._ws || rpc._ws.readyState != rpc._ws.OPEN) {
        return;
    }

    rpc.call(
        'get_meta_data',
        {
            url: iframe.contentWindow.location.pathname,
            full_content_repr: settings.show_full_content_repr,
            internal_meta_data: settings.show_internal_meta_data,
        },
        function(data) {
            ractive.set('content', data);
        }
    );
};

function iframe_onload(iframe) {
    // detect iframe recursion
    if(iframe.contentDocument.body.classList.contains('flamingo-server')) {
        iframe_set_url(iframe.contentWindow.location.href);

        return;
    }

    if(!rpc || !rpc._ws || rpc._ws.readyState != rpc._ws.OPEN) {
        return;
    }

    // history / address
    if(iframe.contentWindow.location.href != 'about:blank') {
        history.pushState({}, iframe.contentDocument.title,
                          iframe.contentWindow.location.href);
    }

    // title
    document.title = iframe.contentDocument.title;

    // favicon
    var nodes = iframe.contentDocument.getElementsByTagName('link');
    var icon = document.querySelector("link[rel='shortcut icon']");

    for(var index = 0; index < nodes.length; index++) {
        if((nodes[index].getAttribute('rel') == 'icon') ||
           (nodes[index].getAttribute('rel') == 'shortcut icon')) {

            icon.href = nodes[index].getAttribute('href');

            break;
        }
    }

    // iframe keyboard shortcuts
    iframe.contentDocument.addEventListener('keydown', function(event) {
        handle_keydown(event);
    });

    // close overlay if iframe gets clicked
    iframe.contentDocument.addEventListener('click', function(event) {
        ractive.set('settings.overlay.open', false);
    });

    iframe_update_meta_data();
};

function iframe_set_url(url) {
    if(url === undefined || url == '') {
        url = '/';
    }

    iframe.contentWindow.location = url;
};

function iframe_reload() {
    iframe.contentWindow.location.reload();
};

function iframe_setup() {
    if(!iframe_initial_setup) {
        iframe_set_url(document.location.href);
        iframe_initial_setup = true;

        return;
    }

    iframe_set_url('about:blank');

    setTimeout(function() {
        iframe_set_url(document.location.href);
    }, 1000);
};

window.onpopstate = function(event) {
    iframe_set_url(document.location.href);
};

window.onhashchange = function(event) {
    iframe_set_url(document.location.href);
};

ractive.observe('settings.show_full_content_repr', function() {
    if(iframe.contentDocument.readyState == 'complete') {
        iframe_update_meta_data();
    }
});

ractive.observe('settings.show_internal_meta_data', function() {
    if(iframe.contentDocument.readyState == 'complete') {
        iframe_update_meta_data();
    }
});

// messages -------------------------------------------------------------------
var message_id = 1;

function hide_message(id) {
    var messages = ractive.get('messages');

    for(var index in messages) {
        if(messages[index].id == id) {
            messages.splice(index, 1);
            ractive.set('messages', messages);

            return;
        }
    }
}

function show_message(message, timeout) {
    var messages = ractive.get('messages');

    for(var index in messages) {
        if(messages[index].message == message) {
            return;
        }
    }

    var id = message_id;
    message_id = id + 1;

    messages.push({
        id: id,
        message: message,
    });

    ractive.set('messages', messages);

    if(timeout != undefined) {
        setTimeout(function() {
            hide_message(id);
        }, timeout);

    }

    return id;
}

ractive.on({
    hide_message: function(event, id) {
        hide_message(id);
    },
});

// Keyboard Shortcuts ---------------------------------------------------------
function handle_keydown(event) {
    var key_code = event.keyCode;

    // ESC
    if(key_code == 27) {
        ractive.fire('toggle_overlay');

        return;
    }

    if(!ractive.get('settings.overlay.open')) {
        return;
    }

    // skip on user input
    if(document.activeElement.tagName == 'INPUT' ||
       document.activeElement.tagName == 'TEXTAREA') {

        return;
    }

    // numbers 1-9
    if(key_code > 48 && key_code < 57) {
        var tab_index = key_code - 48 - 1;
        var tabs = ractive.get('tabs');

        if(tab_index >= tabs.length) {
            return;
        }

        ractive.set('settings.overlay.tab', tabs[tab_index]);
    }
}

document.addEventListener('keydown', function(event) {
    if(!ractive.get('settings.keyboard_shortcuts')) {
        return;
    }

    handle_keydown(event);
});

ractive.on('toggle_overlay', function(event) {
    ractive.set('settings.overlay.open',
                !ractive.get('settings.overlay.open'));
});

// plugin options -------------------------------------------------------------
function set_plugin_option(plugin_name, option_name, value) {
    document.querySelector('#plugin-options').classList.add('disabled');

    rpc.call('set_plugin_option', {
        plugin_name: plugin_name,
        option_name: option_name,
        value: value,

    }, function(data) {
        ractive.set('plugin_options_html', data);
        document.querySelector('#plugin-options').classList.remove('disabled');

    });
}

function reset_plugin_options(plugin_name) {
    document.querySelector('#plugin-options').classList.add('disabled');

    rpc.call('reset_plugin_options', {
        plugin_name: plugin_name,

    }, function(data) {
        ractive.set('plugin_options_html', data);
        document.querySelector('#plugin-options').classList.remove('disabled');

    });
}

function toggle_plugin_help(toggle) {
    var help_div = toggle.parentElement;

    help_div.classList.toggle('hide');
    help_div.classList.toggle('show');
}

// Logging --------------------------------------------------------------------
function add_logger(logger) {
    var settings = ractive.get('settings.log.logger');

    for(var name in logger) {
        if(name in settings) {
            continue;
        }

        settings[name] = name.startsWith('flamingo');
    }

    ractive.set('settings.log.logger', settings);
}

function log_scroll_to_top() {
    document.querySelector('.log .records').scrollTo(0, 0);
}

function log_scroll_to_bottom() {
    document.querySelector('.log .records .scroll-anchor').scrollIntoView();
}

function log_show(level) {
    var records = ractive.get('log.records');

    var settings = {
        level: {
            debug: false,
            info: false,
            warning: false,
            error: false,
            critical: false,
        },
        logger: {},
    };

    settings.level[level] = true;

    for(var index in records) {
        var record = records[index];

        if(record.level == level) {
            settings.logger[record.name] = true;
        }
    }

    ractive.set('settings.log', settings);

    ractive.set('settings.overlay', {
        open: true,
        tab: 'log',
    });
}

ractive.on({
    log_scroll_to_top: function() {
        log_scroll_to_top();
    },
    log_scroll_to_bottom: function() {
        log_scroll_to_bottom();
    },
    log_show: function(event, level) {
        log_show(level);
    },
});

// Connection Handling --------------------------------------------------------
rpc.on('close', function(rpc) {
    ractive.set({
        connected: false,
        log: {},
        plugin_options_html: '',
    });

    setTimeout(function() {
        var dots = ractive.get('dots');
        dots.push('.');

        if(dots.length >= 4) {
            dots = [];
        }

        ractive.set('dots', dots);

        rpc.connect();
    }, 1000);
});

rpc.on('open', function(rpc) {
    iframe_setup();
    ractive.set('connected', true);

    // subscribe to rpc topics
    rpc.subscribe('status', function(data) {
        var pathname = iframe.contentWindow.location.pathname;

        if(data.changed_paths.includes(pathname) ||
           data.changed_paths.includes('*')) {

            iframe_reload();
        }
    });

    rpc.subscribe('messages', function(data) {
        show_message(data, 2000);
    });

    rpc.subscribe('options', function(data) {
        ractive.set('server_options.' + data.name, data.value);
    });

    rpc.subscribe('commands', function(data) {
        if(data.method == 'ractive_set') {
            ractive.set(data.keypath, data.value);

        } else if(data.method == 'ractive_fire') {
            ractive.fire(data.event_name);

        } else if(data.method == 'set_url') {
            iframe_set_url(data.url);

        } else if(data.method == 'reload') {
            iframe_reload();

        }
    });

    // setup logging
    rpc.call('get_options', undefined, function(data) {
        ractive.set('server_options', data);

        rpc._topic_handler.log = function(data) {
            var log = ractive.get('log')

            log.logger = data.logger;
            add_logger(data.logger);

            log.stats = data.stats;

            if(data.initial) {
                log.records = data.records;

            } else {
                log.records = log.records.concat(data.records);

                log.records = log.records.slice(
                    server_options.log_buffer_max_size * -1);
            }

            ractive.set('log', log);
        };

        rpc.call('setup_log', undefined, function(data) {
            add_logger(data.logger);
            ractive.set('log', data);
        });
    });

    // setup plugin options
    rpc.call('get_plugin_options', undefined, function(data) {
        ractive.set('plugin_options_html', data);
    });
});

rpc.connect();
