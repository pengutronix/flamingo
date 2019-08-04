Ractive.DEBUG = false;

function iframe_onload(iframe) {
    // get content meta data
    rpc.call(
        'get_meta_data',
        iframe.contentWindow.location.pathname,
        function(data) {
            ractive.set({
                content_meta_data: data.meta_data,
                content_template_context: data.template_context,
                content_settings: data.settings,
            });
        }
    )

    // url
    ractive.set('iframe_pathname', iframe.contentWindow.location.pathname);
    document.location.hash = iframe.contentWindow.location.pathname;

    // title
    document.title = iframe.contentDocument.title;

    // favicon
    var nodes = iframe.contentDocument.getElementsByTagName('link');

    for(var index = 0; index < nodes.length; index++) {
        if((nodes[index].getAttribute('rel') == 'icon') || (nodes[index].getAttribute('rel') == 'shortcut icon')) {
            document.querySelector("link[rel='shortcut icon']").href = nodes[index].getAttribute('href');
        }
    }

    // page offset
    if(ractive.get('iframe_set_offset')) {
        var offset = ractive.get('iframe_offset');

        iframe.contentWindow.scrollTo(offset[0], offset[1]);
        ractive.set('iframe_set_offset', false);

    } else {
        ractive.set('iframe_offset', [0, 0]);

    }

    iframe.contentWindow.onscroll = function(event) {
        ractive.set('iframe_offset', [this.scrollX, this.scrollY]);
    }

    // keyboard shortcuts
    iframe.contentDocument.addEventListener('keydown', function(event) {
        handle_keydown(event);
    });
}


function iframe_set_url(url) {
    var iframe = document.getElementsByTagName('iframe')[0];

    ractive.set('iframe_set_offset', false);

    if(url == '') {
        ractive.set('iframe_pathname', '/');

    } else {
        iframe.contentWindow.location = url;

    }
}

function get_hash() {
    var hash = document.location.hash;

    if(!hash) {
        return '/';

    }

    return hash.substring(1);
}

function onhashchange() {
    var hash = get_hash();

    if(hash != ractive.get('iframe_pathname')) {
        iframe_set_url(hash);
    }
}

function iframe_reload() {
    var iframe = document.getElementsByTagName('iframe')[0];

    ractive.set('iframe_set_offset', true);
    iframe.contentWindow.location.reload(true);
}

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

var rpc = new RPC('ws://' + window.location.host + '/live-server/rpc/');
var message_id = 1;

var ractive = Ractive({
    target: '#ractive',
    template: '#main',
    data: {
        connected: false,
        iframe_pathname: get_hash(),
        iframe_initial_pathname: get_hash(),
        iframe_set_offset: false,
        iframe_offset: [0, 0],
        overlay: -1,
        overlay_reason: '',
        overlay_heading: '',
        overlay_content: '',
        overlay_tab: 'meta-data',
        log: {
            logger: {},
            records: [],
            level: {},
        },
        content_meta_data: {},
        messages: [],
        settings: {
            keyboard_shortcuts: true,
        },
    },
    computed: {
        selected_log_level: function() {
            var selected_log_level = [];
            var log_level = this.get('log.level')

            if(log_level.debug) {
                selected_log_level.push('DEBUG');
            }

            if(log_level.info) {
                selected_log_level.push('INFO');
            }

            if(log_level.warning) {
                selected_log_level.push('WARNING');
            }

            if(log_level.error) {
                selected_log_level.push('ERROR');
            }

            if(log_level.critical) {
                selected_log_level.push('CRITICAL');
            }

            return selected_log_level;
        },
        selected_logger: function() {
            var selected_logger = [];
            var logger = this.get('log.logger');

            for(var key in logger) {
                if(logger[key]) {
                    selected_logger.push(key);
                }
            }

            return selected_logger;
        }
    }
});

ractive.on({
    toggle_overlay: function(event) {
        if(rpc._ws.readyState == rpc._ws.OPEN) {
            ractive.set({
                overlay: ractive.get('overlay') * -1,
                overlay_reason: 'user',
            });
        }
    },
    reload: function(event) {
        iframe_reload();
    },
    hide_message: function(event, id) {
        hide_message(id);
    },
    start_shell: function(event) {
        rpc.call('start_shell');
    },
    clear_log: function(event) {
        rpc.call('clear_log', undefined, function(data) {
            ractive.set('log.records', []);
        });
    },
});

rpc.on('open', function(rpc) {
    ractive.set({
        connected: true,
        overlay_heading: 'Connected',
        overlay_content: '',
        overlay_tab: 'meta-data',
    });

    if(ractive.get('overlay') > 0 && ractive.get('overlay_reason') == 'reconnect') {
        ractive.set({
            overlay: -1,
            overlay_reason: '',
        });
    }

    rpc.subscribe('status', function(data) {
        var iframe = document.getElementsByTagName('iframe')[0];

        if(data.changed_paths.includes(iframe.contentWindow.location.pathname) ||
            data.changed_paths.includes('*')) {

            iframe_reload();

            if(ractive.get('overlay_reason') == 'log') {
                ractive.set('overlay', -1);
            }
        }
    });

    rpc._topic_handler.log = function(data) {
        var records = ractive.get('log.records').concat(data.records);
        var logger = ractive.get('log.logger');

        for(var index in data.logger) {
            var logger_name = data.logger[index];

            if(logger.hasOwnProperty(logger_name)) {
                continue;
            }

            logger[logger_name] = logger_name.startsWith('flamingo');
        }

        records = records.slice(-2500);

        for(var index in records) {
            if(records[index].level == 'ERROR' && ractive.get('overlay') < 0) {
                ractive.set({
                    overlay: 1,
                    overlay_reason: 'log',
                    overlay_tab: 'log',
                });
            }
        }

        ractive.set('log.logger', logger);
        ractive.set('log.records', records);
    };

    rpc.call('setup_log', undefined, function(data) {
        var logger = {};

        for(var index in data.logger) {
            var logger_name = data.logger[index];

            logger[logger_name] = logger_name.startsWith('flamingo');
        }

        ractive.set('log.records', data.records);
        ractive.set('log.logger', logger);

        ractive.set('log.level', {
            debug: false,
            info: false,
            warning: true,
            error: true,
            critical: true,
        });
    });

    rpc.subscribe('messages', function(data) {
        show_message(data, 2000);
    });

    iframe_reload();
});

function reconnect() {
    var counter = 5;

    function tick() {
        if(counter > -1) {
            ractive.set('overlay_content', 'trying to reconnect in ' + counter + ' seconds');
            counter--;

            setTimeout(function() {
                tick();
            }, 1000);

        } else {
            rpc.connect();

        }
    }

    tick();
}

rpc.on('close', function(rpc) {
    ractive.set({
        connected: false,
        overlay_heading: 'Connection lost',
        overlay_tab: '',
        log: {
            logger: {},
            records: [],
            level: {},
        },
    });

    if(ractive.get('overlay') < 0) {
        ractive.set({
            overlay: 1,
            overlay_reason: 'reconnect',
        });
    }

    reconnect();
});

rpc.connect();

// keyboard shortcuts
function handle_keydown(event) {
    function set_tab(name) {
        if(ractive.get('overlay') > 0) {
            ractive.set('overlay_tab', name);
        }
    }

    if(!ractive.get('settings.keyboard_shortcuts')) {
        return;
    }

    switch(event.keyCode) {
        case 27:  // ESC
            ractive.fire('toggle_overlay');
            break;

        case 49:  // 1
            set_tab('meta-data');
            break;

        case 50:  // 2
            set_tab('template-context');
            break;

        case 51:  // 3
            set_tab('project-settings');
            break;

        case 52:  // 4
            set_tab('log');
            break;
    }
}

document.addEventListener('keydown', function(event) {
    handle_keydown(event);
});
