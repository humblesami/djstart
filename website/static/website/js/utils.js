var json_utils = {
    sort_list_by_prop: function(arrayOfObjects, prop_name){
        var byDate = arrayOfObjects.slice(0);
        byDate.sort(function(a,b) {
            return a[prop_name] - b[prop_name];
        });
        return byDate;
    },

    add_delete_url_param: function(){

    },
    loadExternalResource: function (resourceUrl, elem, time_out=5000){
        var fetchTimer = undefined;
        function completeResourceFetch(reason, html) {
            console.log('Completed with ' + reason);
            elem.innerHTML = html || '';
            clearTimeout(fetchTimer);
        }
        function loadViaXhr(resourceUrl, onLoad, onError){
            var xhr = new XMLHttpRequest();
            fetchTimer = setTimeout(function() {
                onError('Time out');
                xhr.abort();
            }, time_out);
            try {
                xhr.onload = function(resp) {
                    var xmlString = resp.srcElement.responseText;
                    onLoad('Done', xmlString);
                };
                xhr.open("GET", resourceUrl, true);
                xhr.send();
            } catch (e) {
                onError(e);
            }
        }
        loadViaXhr(resourceUrl,completeResourceFetch, completeResourceFetch);
        console.log('Started');
    }
}