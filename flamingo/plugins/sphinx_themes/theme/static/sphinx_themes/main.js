window.addEventListener('load', function() {
    var mark_name = get_get_variable('mark') || get_get_variable('q');

    if(!mark_name) {
      return;
    }

    var context = document.querySelector(search_ractive_target_selector);
    var mark = new Mark(context);

    mark.mark(mark_name);
});
