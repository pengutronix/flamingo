function iframe_set_url(url) {
    var iframe = document.getElementsByTagName('iframe')[0];

    if(url == '') {
        ractive.set('iframe_pathname', '/');
    } else {
        iframe.contentWindow.location = url;
    }
}

function iframe_reload() {
    var iframe = document.getElementsByTagName('iframe')[0];

    iframe.contentWindow.location.reload(true);
}

var rpc = new RPC('ws://' + window.location.host + '/live-server/rpc/');

var ractive = Ractive({
    target: '#ractive',
    template: '#main',
    data: {
        iframe_pathname: '/',
        overlay: -1,
        overlay_reason: '',
        overlay_heading: '',
        overlay_content: '',
        log: [],
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
    rebuild: function(event) {
        ractive.set('overlay_content', 'rebuilding full site...');

        rpc.call('rebuild', undefined, function(data) {
            ractive.set('overlay_content', 'site rebuild successful');
        
        },
        function(data) {
            ractive.set('overlay_content', 'rebuild failed');

        });
    },
    toggle_index: function(event) {
        rpc.call('toggle_index', undefined, function(data) {
            ractive.set('overlay_content', 'index is ' + (data ? 'enabled':'disabled'));
            iframe_reload();

        },
        function(data) {
            ractive.set('overlay_content', 'internal error');

        });
    },

});

rpc.on('open', function(rpc) {
    ractive.set({
        overlay_heading: 'Connected',
        overlay_content: '',
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
            ractive.set('log', []);

            if(ractive.get('overlay_reason') == 'log') {
                ractive.set('overlay', -1);
            }
        }
    });

    rpc.subscribe('log', function(data) {
        var log = ractive.get('log').concat(data);

        log = log.slice(-100);
        ractive.set('log', log);

        for(index in ractive.get('log')) {
            if(log[index].level == 'ERROR' && ractive.get('overlay') < 0) {
                ractive.set({
                    overlay: 1,
                    overlay_reason: 'log',
                });
            }
        }
    });
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
        overlay_heading: 'Connection lost',
        log: [],
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
