function get_get_variable(name) {
    var urlParams = new URLSearchParams(window.location.search);
    var entries = urlParams.entries();

    for(entry of entries) {
        if(entry[0] == name) {
            return entry[1];
        }
    }

    return '';
}
