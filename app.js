let lastSong = ''; // To track the last song that was shown on the webpage

// Fetch the current song data from current_track.txt
async function fetchSongData() {
    try {
        console.log("Fetching song data...");
        const response = await fetch(`current_track.txt?timestamp=${Date.now()}`); // Use Date.now() to ensure fresh fetch
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const textData = await response.text();

        if (!textData || textData.trim() === "") {
            console.warn("Empty or malformed current_track.txt file.");
            return;
        }

        const lines = textData.split('\n').filter(line => line.trim() !== "");
        let track = '';
        let band = '';

        lines.forEach(line => {
            if (line.startsWith('Band:')) {
                band = line.replace('Band:', '').trim();
            } else if (line.startsWith('Track:')) {
                track = line.replace('Track:', '').trim();
            }
        });

        const currentSong = `${band} - ${track}`;

        // Only update if the song has changed
        if (currentSong !== lastSong) {
            lastSong = currentSong; // Update the last song
            console.log("New song detected:", currentSong);

            // Update the song info on the page
            document.getElementById('song-title').textContent = `Track: ${track}`;
            document.getElementById('song-band').textContent = `Band: ${band}`;

            // Fetch and update album art
            await fetchAlbumArt(); // Wait for album art to be fetched

            // Fetch and update recently played songs
            fetchRecentlyPlayed();

            // Update the media session metadata (for Android notifications, etc.)
            if ('mediaSession' in navigator) {
                navigator.mediaSession.metadata = new MediaMetadata({
                    title: track,
                    artist: band,
                    artwork: [
                        { src: document.getElementById('album-art').src, sizes: '512x512', type: 'image/png' }
                    ]
                });
            }
        }
    } catch (error) {
        console.error('Error fetching song data:', error);
    }
}

// Fetch album art from the server with cache-busting and retry logic
async function fetchAlbumArt(retries = 3) {
    const possibleExtensions = ['jpg', 'png', 'gif', 'jpeg', 'webp'];
    let mostRecentArtUrl = null;

    // Introduce a delay to ensure the album art has time to update
    await new Promise(resolve => setTimeout(resolve, 3000));  // 3-second delay

    for (let ext of possibleExtensions) {
        try {
            const artResponse = await fetch(`art.${ext}?timestamp=${Date.now()}`); // Cache-bust
            if (artResponse.ok) {
                mostRecentArtUrl = `art.${ext}?timestamp=${Date.now()}`;
                break;
            }
        } catch (error) {
            console.warn(`Error fetching art.${ext}:`, error);
        }
    }

    // If no art is found, retry with reduced retries
    if (!mostRecentArtUrl && retries > 0) {
        console.log(`Retrying fetchAlbumArt... Retries left: ${retries}`);
        await new Promise(resolve => setTimeout(resolve, 2000));  // Wait for 2 seconds before retrying
        return fetchAlbumArt(retries - 1);  // Retry with reduced attempts
    }

    // Fallback to default art if no new art is found after retries
    if (!mostRecentArtUrl) {
        mostRecentArtUrl = 'default-art.png';
        console.warn("Using default album art.");
    }

    // Update the album art
    document.getElementById('album-art').src = mostRecentArtUrl;
    console.log("Album art updated to:", mostRecentArtUrl);
}

// Fetch the last 10 songs from last10.txt
async function fetchRecentlyPlayed() {
    try {
        console.log("Fetching recently played songs...");
        const response = await fetch(`last10.txt?timestamp=${Date.now()}`); // Cache-bust
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const textData = await response.text();
        const recentSongs = textData.split('\n').filter(song => song.trim() !== "");

        // Update the HTML to display the last 10 songs
        const recentSongsList = document.getElementById('recent-songs-list');
        recentSongsList.innerHTML = '';  // Clear the list

        recentSongs.forEach(song => {
            const li = document.createElement('li');
            li.textContent = song;
            recentSongsList.appendChild(li);
        });
        console.log("Recently played list updated.");
    } catch (error) {
        console.error('Error fetching recently played songs:', error);
    }
}

// Fetch song data every 10 seconds to keep the page updated
setInterval(fetchSongData, 10000);

// Fetch recently played songs every 60 seconds (in case the file updates without song change)
setInterval(fetchRecentlyPlayed, 60000);

// Initial fetch
fetchSongData();
fetchRecentlyPlayed();
