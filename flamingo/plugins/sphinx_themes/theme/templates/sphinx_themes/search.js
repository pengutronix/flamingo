window.addEventListener('load', function() {
    // setup ractive
    search_ractive = Ractive({
        target: search_ractive_target_selector,
        template: search_ractive_template,
        data: {
            query: '',
            results: [],
        },
    });

    // setup search index
    search_index = elasticlunr(function() {
        this.setRef('id');
        this.addField('title');
        this.addField('body');
    });

    {% for content in context.contents %}
        search_index.addDoc({
            id: '{{ content.output }}',
            title: {{ safe_dump(content.content_title) }},
            body: {{ safe_dump(content.content_body) }},
        });
    {% endfor %}

    // setup query
    var query = get_get_variable('q');

    if(query) {
        search_ractive.set({
            query: query,
            results: search_index.search(query),
        });
    };
});
