(function () {

    const loc_obj = window.location;
    const server_url = loc_obj.origin + '';

    function activate_purge(){
        $('#purge-menu a.purge').click(function(){
            let el = $(this);
            let file_path = '';
            let purge_req_options = {
                url: server_url + '/purge/cache',
                dataType: 'json',
                contentType: "application/json",
                type: "POST",
                success: function(data){
                    if(data.result){
                        if (typeof(data.result) == 'string'){
                            data = JSON.parse(data.result);
                        }
                    }
                    console.log('purge response', data);
                    if(data.data){
                        data = data.data;
                    }
                    if(data.error){
                        data = data.error;
                    }
                    console.log(data + ', Please now open page in incognitive yo be cached');
                },
                error: function(e){
                    console.log(' Error in purge => ', e.responseText, purge_req_options.url);
                }
            }
            let purge_urls_server = 'https://www.balochistantimes.pk';
            let ar_purge_files = get_files_to_purge(el, purge_urls_server);
            if (!ar_purge_files.length){
                return;
            }
            purge_req_options.data = JSON.stringify({urls:ar_purge_files});
            $.ajax(purge_req_options);
        });
    }

    function get_files_to_purge(el, purge_urls_server){
        let ar_purge_files = [];
        if(el.hasClass('all')){
            ar_purge_files = ['all'];
        }
        if(el.hasClass('home')){
            ar_purge_files = [purge_urls_server];
        }
        else if(el.hasClass('current')){
            ar_purge_files = [purge_urls_server + window.location.pathname];
        }
        else if(el.hasClass('images')){
            let css_files = $(document).find('img');
            css_files.each(function(i, el){
                file_path = el.src;
                if(file_path)
                {
                    if(file_path.startsWith(server_url))
                    {
                        file_path = file_path.substr(server_url.length);
                    }
                    file_path = purge_urls_server + file_path;
                    ar_purge_files.push(file_path);
                }
            });
            if(!ar_purge_files.length)
            {
                alert('No image files to purge');
            }
        }
        else if(el.hasClass('static')){
            let css_files = $(document).find('link[rel="stylesheet"]');
            let js_files = $(document).find('script');
            let files = [];
            css_files.each(function(i, el){
                file_path = el.href;
                if(file_path)
                {
                    if(file_path.startsWith(server_url))
                    {
                        file_path = file_path.substr(server_url.length)
                    }
                    file_path = purge_urls_server + file_path;
                    ar_purge_files.push(file_path);
                }
            });
            js_files.each(function(i, el){
                file_path = el.src;
                if(file_path)
                {
                    if(file_path.startsWith(server_url))
                    {
                        file_path = file_path.substr(server_url.length)
                    }
                    file_path = purge_urls_server + file_path;
                    ar_purge_files.push(file_path);
                }
            });
            if(!ar_purge_files.length)
            {
                alert('No static files to purge');
            }
        }
        return ar_purge_files;
    }

    function enable_background_image_in_edit(){
        odoo.define('website_base.rte', function (require) {
            var RTEWidget = require('web_editor.rte').Class;
            RTEWidget.include({
                start: function(){
                    const res = this._super.apply(this, arguments);
                    let images = $('img.img_cover_image').css('z-index', -1);
                    images.each(function(i, el){
                        $(el).parent().css('background-image', 'url("'+el.src+'")');
                    });
                    return res;
                }
            })
        });
    }

    function set_image_heights(){
        let image_parents = document.querySelectorAll('.o_record_cover_image:not(.adjusted)');
        for(let el of image_parents){
            let el_width = el.getBoundingClientRect().width;
            if(!el_width){
                el_width = el.parentNode.getBoundingClientRect().width;
            }
            if(!el_width){
                console.log('Element has no width');
                return;
            }
            else{
                el_width = parseFloat(el_width);
            }
            if(!el.style.height){
                let height = el_width * 0.587;
                let height_to_apply = height + 'px';
                el.classList.add("adjusted");
                el.style.height = height_to_apply;
            }
            if(el.nextElementSibling) { el.nextElementSibling.remove(); }
            if(el.nextElementSibling) { el.nextElementSibling.remove(); }
            el.classList.remove("o_record_cover_component");
            el.parentNode.classList.remove("o_half_screen_height")
            el.parentNode.classList.remove("o_full_screen_height");
        }
        //console.log('Setting heights of => '+els.length+' images');
    }

    function add_user_menus(uid){
        let user_class = 'o_connected_user';
        if(!isNaN(uid)){
            console.log('Staff');
            $('#purge-menu').hide();
            if($('#purge-menu a.purge').length)
            {
                activate_purge();
                $('#purge-menu').show();
            }
            let user_menu_bar = $('#oe_main_menu_navbar').show();
            if(!$('body').hasClass(user_class))
            {
                $('body').addClass(user_class);
            }
            $('body a').each(function(i, el){
                if(el.href && !el.href.endsWith('#')){
                    if(!el.href.endsWith('staff=1')){
                        if(el.href.indexOf('?') > -1){
                            el.href = el.href + '&staff=1';
                        }
                        else{
                            el.href = el.href + '?staff=1';
                        }
                    }
                    //console.log(i, el.href);
                }
            });
            $('button[data-target="#top_menu_collapse"],#edit-page-menu').css('visibility', 'visible');
            if(!window.enable_bg_image_edit){
                window.enable_bg_image_edit = 1;
                enable_background_image_in_edit();
            }
            else{
                console.log('Bg edit Already enabled');
            }
        }
        else{
            console.log('Public');
            if($('body').hasClass(user_class))
            {
                $('body').removeClass(user_class);
            }
        }
    }

    function on_page_full_ready(){
        set_image_heights();
        $('.spinner').hide(); $('#wrapwrap').css('visibility', 'visible');
    }

    function after_css_rendered(with_message){
        console.log('Showing dom after all done from => '+with_message);
        $('#wrapwrap').css('visibility', 'hidden').show();
        let image_parents = document.querySelectorAll('.o_record_cover_image:not(.adjusted)');
        if(!image_parents.length){
            console.log('No images found');
            on_page_full_ready();
            return;
        }
        const body_width = document.body.getBoundingClientRect().width;
        const first_parent_width = image_parents[0].getBoundingClientRect().width;
        if(first_parent_width != body_width){
            on_page_full_ready();
            return;
        }
        let cnt = 0;
        let cnt_limit = 20;
        if(with_message == 'after time out 2500')
        {
            cnt_limit = 10;
        }
        const css_waiter = setInterval(function(){
            cnt += 1;
            if(cnt >= cnt_limit || image_parents[0].clientWidth != body_width){
                console.log('Ready after '+cnt+ ' waits');
                clearInterval(css_waiter);
                on_page_full_ready();
                return;
            }
        }, 100);
    }

    //after_css_rendered();

    set_image_heights();
})();