jQuery(function($) {
    $(document).ready(function() {
        $("select#title").change(function() {
            if ($(this).val() != 'Z') {
                var title = $(this).val();
                var new_url = "/addEdition/" + $(this).val() + "/";
                $('#add_edition').attr('href', new_url);
                var add_edition=document.getElementById('add_edition');
                add_edition.classList.remove('hidden');
                var url = "/title/" + $(this).val() + "/";
                $.getJSON(url, function(editions) {
                    var options = '<option value="Z">select an edition</option>';
                    for (var i = 0; i < editions.length; i++) {
                        options += '<option value="' + editions[i]['id'] + '">Edition ' + editions[i]['Edition_number'] + '</option>';
                    }
                    $("select#edition").html(options);
                    $("select#edition option:first").attr('selected', 'selected');
                });
                $("select#issue")
                    .empty()
            }
        });

        $("select#edition").change(function(vent) {
            if ($(this).val() != 'Z') {
                var edition = $(this).val();
                var new_url = "/addIssue/" + $(this).val() + "/";
                $('#add_issue').attr('href', new_url);
                var add_issue=document.getElementById('add_issue');
                add_issue.classList.remove('hidden');
                var url = "/edition/" + $(this).val() + "/";
                $.getJSON(url, function(issues) {
                    var options = '<option value="Z">select an issue</option>';
                    for (var i = 0; i < issues.length; i++) {
                        options += '<option value="' + issues[i]['id'] + '">Issue ' + issues[i]['STC_Wing'] + '</option>';
                    }
                    $("select#issue").html(options);
                    $("select#issue option:first").attr('selected', 'selected');
                });
            }
        });
    });
});
