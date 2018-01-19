function showAddAnotherPopup(triggeringLink) {
    var href = triggeringLink.href;
    var name = triggeringLink.name;
    var win = window.open(href, name, "height=500,width=800,resizable=yes,scrollbars=yes");
    win.focus();
    return false;
}

function dismissAddAnotherTitle(win, newId, newTitle) {
    var x = document.getElementById('title');
    var option = document.createElement("option");
    option.text = newTitle;
    option.value = newId;
    option.selected = true;
    x.add(option);

    var editions = document.getElementById('edition');
    editions.options.length = 0;

    var issues = document.getElementById('issue');
    issues.options.length = 0;

    var new_url = "/addEdition/" + newId + "/";
    var add_edition=document.getElementById('add_edition');
    add_edition.classList.remove('hidden');
    add_edition.href = new_url;
    win.close();
}

function dismissAddAnotherEdition(win, newId, newEdition) {
    var x = document.getElementById('edition');
    var option = document.createElement("option");
    option.text = "Edition "+ newEdition;
    option.value = newId;
    option.selected = true;
    x.add(option);

    var issues = document.getElementById('issue');
    issues.options.length = 0;

    var new_url = "/addIssue/" + newId + "/";
    var add_issue=document.getElementById('add_issue');
    add_issue.classList.remove('hidden');
    add_issue.href = new_url;
    win.close();
}

function dismissAddAnotherIssue(win, newId, newIssue) {
    var x = document.getElementById('issue');
    var option = document.createElement("option");
    option.text = "Issue " + newIssue;
    option.value = newId;
    option.selected = true;
    x.add(option);
    win.close();
}
