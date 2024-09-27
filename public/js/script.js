function stopMusic() {
  button = document.getElementById("stopButton");
  player = document.getElementById("mediaPlayer");
  if (player.paused) {
    player.play();
    button.innerHTML = '<span class="nf nf-md-pause"></span>&nbsp;' + button.innerHTML.split("&nbsp;", 2)[1].trim();
  } else {
    player.pause();
    button.innerHTML = '<span class="nf nf-md-play"></span>&nbsp;' + button.innerHTML.split("&nbsp;", 2)[1].trim();
  }
  return false;
}

function playMusic(name) {
  var song = manifest[name];
  if (!song) {
    console.log('Could not find song "' + name + '"');
    return false;
  }
  player = document.getElementById("mediaPlayer");
  player.pause();
  player.src = song.file;
  player.play();
  document.title = "🎶" + name;
  window.location.hash = name;
  button = document.getElementById("stopButton");
  button.innerHTML = '<span class="nf nf-md-pause"></span>&nbsp;' + name;
  button.style.display = "block";
  return false;
}

function filterMusic() {
  var input, filter, ul, li, a, i, txtValue;
  input = document.getElementById("mediaInput");
  filter = input.value.toUpperCase();
  ul = document.getElementById("audio-list");
  li = ul.getElementsByTagName("a");

  // Loop through all list items, and hide those who don't match the search query
  for (i = 0; i < li.length; i++) {
    a = li[i]; //.getElementsByTagName("a")[0];
    txtValue = a.textContent || a.innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      li[i].style.display = "";
    } else {
      li[i].style.display = "none";
    }
  }
}
function clearFilter() {
  input = document.getElementById("mediaInput");
  input.value = "";
  filterMusic();
  return false;
}

function combatFilter() {
  input = document.getElementById("mediaInput");
  input.value = "Initiative";
  filterMusic();
  return false;
}

function handleHashChange() {
  // Extract the hash from the URL without the '#' prefix
  let songName = decodeURIComponent(window.location.hash.slice(1));
  if (!songName) return;
  input = document.getElementById("mediaInput");
  input.value = songName;
  document.title = "🎶" + songName;
  filterMusic();
}

function processManifest() {
  let audioTemplate = document.getElementById("audio-template");
  let template = Handlebars.compile(audioTemplate.innerHTML);
  document.getElementById("audio-list").innerHTML = template(manifest);
}

window.addEventListener("load", processManifest);
window.addEventListener("load", handleHashChange);
//window.addEventListener("hashchange", handleHashChange);
