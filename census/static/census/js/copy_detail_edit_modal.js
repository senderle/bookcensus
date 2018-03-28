jQuery(function($) {
    $(document).ready(function() {
        $(".copy_data").unbind('click');
        $(".copy_data").click(function(ev) {
            ev.preventDefault();
            var url=$(this).data("form");
            $("#copyModal").load(url, function() {
                $("#copyModal").modal('show');
                $(document).click(function(ev) {
                    if (! $(event.target).closest(".modal-dialog").length) {
                    	$("#copyModal").modal('hide');
                    }
                });
            });
            return false;
        });

        $(".update_copy").unbind('click');
        $(".update_copy").click(function(ev) {
            ev.preventDefault();
            var url=$(this).data("form");
            $("#editModal").load(url, function() {
                $("#editModal").modal('show');
            });
            return false;
        });

        $(".update_childcopy").unbind('click');
        $(".update_child_copy").click(function(ev) {
            ev.preventDefault();
            var url=$(this).data("form");
            $("#editChildModal").load(url, function() {
                $("#editChildModal").modal('show');
            });
            return false;
        });

        $(".title_data").unbind('click');
        $(".title_data").click(function(ev) {
            ev.preventDefault();
            var url=$(this).data("form");
            $("#titleModal").load(url, function() {
                $("#titleModal").modal('show');
            });
            return false;
        });

        $(".edition_data").unbind('click');
        $(".edition_data").click(function(ev) {
            ev.preventDefault();
            var url=$(this).data("form");
            $("#editionModal").load(url, function() {
                $("#editionModal").modal('show');
            });
            return false;
        });

        $(".issue_data").unbind('click');
        $(".issue_data").click(function(ev) {
            ev.preventDefault();
            var url=$(this).data("form");
            $("#issueModal").load(url, function() {
                $("#issueModal").modal('show');
            });
            return false;
        });

        $(".update_title").unbind('click');
        $(".update_title").click(function(ev) {
            ev.preventDefault();
            var url=$(this).data("form");
            $("#titleUpdateModal").load(url, function() {
                $("#titleUpdateModal").modal('show');
            });
            return false;
        });

        $(".update_edition").unbind('click');
        $(".update_edition").click(function(ev) {
            ev.preventDefault();
            var url=$(this).data("form");
            $("#editionUpdateModal").load(url, function() {
                $("#editionUpdateModal").modal('show');
            });
            return false;
        });

        $(".update_issue").unbind('click');
        $(".update_issue").click(function(ev) {
            ev.preventDefault();
            var url=$(this).data("form");
            $("#issueUpdateModal").load(url, function() {
                $("#issueUpdateModal").modal('show');
            });
            return false;
        });


    });
});

function generateDialog(copy_id) {
    $.ajax({
        url: $('.editForm').attr('action'),
        type: "POST",
        datatype: "json",
        data: $('.editForm').serialize(),
        async: true,
        success: function(data) {
            if(data['stat'] === "ok") {
                alert('Success! Your changes have been saved.');
                $("#editModal").modal('hide');
                window.location.reload();
            } else {
                alert("Error: invalid input! Please correct the errors in your input and submit again!");
                $("#editModal").html(data['form']);
                if(data['stat']==='title error') {
                    var option = $('#title').val('Z');
                    option.selected = true;
                    var editions = document.getElementById('edition');
                    editions.options.length = 0;
                    var issues = document.getElementById('issue');
                    issues.options.length = 0;
                    var add_edition=document.getElementById('add_edition');
                    add_edition.classList.add('hidden');
                    var add_issue=document.getElementById('add_issue');
                    add_issue.classList.add('hidden');

                } else if (data['stat'] ==='edition error') {
                    var option = $('#edition').val('Z');
                    option.selected = true;
                    var issues = document.getElementById('issue');
                    issues.options.length = 0;

                    var add_issue=document.getElementById('add_issue');
                    add_issue.classList.add('hidden');
                } else if (data['stat'] === 'issue error') {
                    var option = $('#issue').val('Z');
                    option.selected = true;
                }
                $("#editModal").modal('show');
            }
        }
    });
    return false;
}

function genTitleDialog(title_id) {
    $.ajax({
        url: $('.editForm').attr('action'),
        type: "POST",
        datatype: "json",
        data: $('.editForm').serialize(),
        async: true,
        success: function(data) {
            if(data['stat'] === "ok") {
                alert('Success! Your changes have been saved.');
                $("#titleUpdateModal").modal('hide');
                window.location.reload();
            } else {
                alert("Error: invalid input! Please correct the errors in your input and submit again!");
                $("#titleUpdateModal").html(data['form']);
                $("#titleUpdateModal").modal('show');
            }
        }
    });
    return false;
}

function genEditionDialog(edition_id) {
    $.ajax({
        url: $('.editForm').attr('action'),
        type: "POST",
        datatype: "json",
        data: $('.editForm').serialize(),
        async: true,
        success: function(data) {
            if(data['stat'] === "ok") {
                alert('Success! Your changes have been saved.');
                $("#editionUpdateModal").modal('hide');
                window.location.reload();
            } else {
                alert("Error: invalid input! Please correct the errors in your input and submit again!");
                $("#editionUpdateModal").html(data['form']);
                $("#editionUpdateModal").modal('show');
            }
        }
    });
    return false;
}

function genIssueDialog(issue_id) {
    $.ajax({
        url: $('.editForm').attr('action'),
        type: "POST",
        datatype: "json",
        data: $('.editForm').serialize(),
        async: true,
        success: function(data) {
            if(data['stat'] === "ok") {
                alert('Success! Your changes have been saved.');
                $("#issueUpdateModal").modal('hide');
                window.location.reload();
            } else {
                alert("Error: invalid input! Please correct the errors in your input and submit again!");
                $("#issueUpdateModal").html(data['form']);
                $("#issueUpdateModal").modal('show');
            }
        }
    });
    return false;
}
