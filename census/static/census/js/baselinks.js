var links = document.getElementById('links');
var home_link = document.getElementById('homelink');
var titles_link = document.getElementById('titleslink');
var copy_link = document.getElementById('copylistlink');
var submission_link = document.getElementById('submissionlink');
var profile_link = document.getElementById('profilelink');
var history_link = document.getElementById('historylink');
var logout_link = document.getElementById('logoutlink');
var login_link = document.getElementById('loginlink');
var account = document.getElementById('dropdownMenu');

var url = window.location.href;

if (url.indexOf('search') > -1) {
  copy_link.classList.remove('not.active');
  copy_link.classList.add('active');

} else if (url.indexOf('view_submitted_copies') > -1){
  account.classList.add('active');
  history_link.classList.add('active2');

} else if (url.indexOf('titles') > -1 || url.indexOf('editions') > -1 || url.indexOf('issue') > -1) {
  titles_link.classList.remove('not.active');
  titles_link.classList.add('active');

} else if (url.indexOf('addTitle') > -1
          || url.indexOf('addEdition') > -1 || url.indexOf('addIssue') > -1
          || url.indexOf('welcome') > -1) {
  links.classList.add('hidden');

} else if (url.indexOf('submission') > -1) {
  submission_link.classList.remove('not.active');
  submission_link.classList.add('active');

} else if (url.indexOf('copy') > -1 || url.indexOf('copies') > -1
          ||url.indexOf('transactions') > -1 ||url.indexOf('search') > -1) {
  copy_link.classList.remove('not.active');
  copy_link.classList.add('active');

} else {
  account.classList.add('active');
  if (url.indexOf('profile') > -1 || url.indexOf('Profile') > -1) {
    profile_link.classList.add('active2');
  } else if (url.indexOf('history') > -1) {
    history_link.classList.add('active2');
  } else if (url.indexOf('login') > -1) {
    login_link.classList.add('active2');
  } else if (url.indexOf('logout') > -1) {
    logout_link.classList.add('active2');
  }
}
