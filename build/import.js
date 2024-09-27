let ASSETS_URL = "https://ttaudio.seansbox.com/";

async function importTabletopAudio() {
  ui.notifications.info("Tabletop Audio importing...");

  let manifest = null;
  try {
    manifest = await fetch(ASSETS_URL + "build/manifest.json");
    if (!manifest.ok) {
      throw new Error("Failed to fetch manifest.json");
    }
    manifest = await manifest.json();
  } catch (error) {
    console.error("Error fetching data:", error);
    ui.notifications.error("Failed to fetch Tabletop Audio data. Please check your internet connection.");
    return; // Exit the function if there's an error in fetching data
  }
  let sounds = manifest.sounds;
  delete manifest.sounds;

  let playlist = game.playlists.find((p) => p.name === "Tabletop Audio");
  if (!playlist) {
    playlist = await Playlist.create(manifest, { renderSheet: false });
  } else {
    await playlist.update(manifest, { renderSheet: false });
  }

  const playlistSoundsMap = new Map(playlist.sounds.map((s) => [s.name, s]));

  console.log(sounds);

  for (const sound of sounds) {
    sound.path = ASSETS_URL + sound.path;
    const playlistSound = playlistSoundsMap.get(sound.name);
    if (playlistSound) {
      console.log(`Updating ${sound.name}`);
      await playlistSound.update(sound, { renderSheet: false });
    } else {
      console.log(`Creating ${sound.name}`);
      await playlist.createEmbeddedDocuments("PlaylistSound", [sound], { renderSheet: false });
    }
  }

  ui.notifications.info("Tabletop Audio imported!");
}

await importTabletopAudio();
console.log("Done");
