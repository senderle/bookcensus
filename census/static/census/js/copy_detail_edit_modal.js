jQuery(function($) {
    $(document).ready(function() {
        $(".copy_data").unbind('click');
        $(".copy_data").click(function(ev) {
            ev.preventDefault();
            var url=$(this).data("form");
            $("#copyModal").load(url, function() {
                $("#copyModal").modal('show');
                $(document).click(function(event) {
                    if (! $(event.target).closest(".modal-dialog").length) {
                    	$("#copyModal").modal('hide');
                    }
                });
            });
            return false;
        });

        var copy_nsc = '';
        var pathlist = window.location.pathname
            .replace(/^\/*/, '')
            .replace(/\/*$/, '')
            .split('/');
        if (pathlist.length == 2 && 
                pathlist[0] === 'sc' && 
                pathlist[1].match(/^[0-9]+$/)) {
            copy_nsc = pathlist[1];
        } else if (window.location.hash) {
            copy_nsc = window.location.hash.substring(1);
        }

        if (copy_nsc !== '') {
            $(".copy_data_" + copy_nsc).click();
        }
    });
});
