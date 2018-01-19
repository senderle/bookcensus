jQuery(function($) {
$(document).ready(function() {
  var copy_submit=document.getElementById('copy_submit');

  $("select#title").change(function() {
    if ($(this).val() == 'Z') {
      $('.edition_section').attr('style', 'display:none');
      $('.issue_section').attr('style', 'display:none');
      $('.copy_section').attr('style', 'display:none');
      copy_submit.style.display="none";
    }
    else {
      $('.edition_section').attr('style', 'display:inline');
      var title = $(this).val();
      var new_url = "/addEdition/" + $(this).val() + "/";
      $('#add_edition').attr('href', new_url);
      var url = "/title/" + $(this).val() + "/";
      $.getJSON(url, function(editions) {
        var options = '<option value="Z">select an edition</option>';
        for (var i = 0; i < editions.length; i++) {
          options += '<option value="' + editions[i]['id'] + '">Edition ' + editions[i]['Edition_number'] + '</option>';
        }
        $("select#edition").html(options);
        $("select#edition option:first").attr('selected', 'selected');
      });
    }
  });

  $("select#edition").change(function(vent) {
    if ($(this).val() == 'Z') {
      $('.issue_section').attr('style', 'display:none');
      $('.copy_section').attr('style', 'display:none');
      copy_submit.style.display="none";
    }
    else {
      $('.issue_section').attr('style', 'display:inline');
      var edition = $(this).val();
      var new_url = "/addIssue/" + $(this).val() + "/";
      $('#add_issue').attr('href', new_url);
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

	$("select#issue").change(function(vent) {

    if ($(this).val() == 'Z') {
			$('.copy_section').attr('style', 'display:none');
  		copy_submit.style.display="none";
		}
		else {
			$('.copy_section').attr('style', 'display:inline');
  		copy_submit.style.display="inline";
		}
	});
});
});
