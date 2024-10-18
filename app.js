async function fetchSongData() {
    try {
        console.log("Fetching song data...");
        // Add a timestamp to prevent caching
        const response = await fetch(`current_track.txt?timestamp=${new Date().getTime()}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const textData = await response.text();
        console.log("Text data fetched:", textData);

        // If the file is empty or doesn't contain any useful data
        if (!textData || textData.trim() === "") {
            console.warn("Empty or malformed current_track.txt file.");
            return;
        }

        // Parse the text data: first Band, then Track (instead of Title)
        const lines = textData.split('\n').filter(line => line.trim() !== ""); // Filter out empty lines
        let track = '';
        let band = '';

        // Safeguard against missing fields in the file
        lines.forEach(line => {
            if (line.startsWith('Band:')) {
                band = line.replace('Band:', '').trim();
            } else if (line.startsWith('Track:')) {
                track = line.replace('Track:', '').trim();
            }
        });

        // If no band or track is found, log an error
        if (!band || !track) {
            console.error("Band or Track data missing in current_track.txt.");
            return;
        }

        // Check for art files with various extensions and get their Last-Modified header
        const possibleExtensions = ['jpg', 'png', 'gif', 'jpeg', 'webp'];
        let mostRecentArtUrl = null;
        let mostRecentDate = new Date(0);  // Set the initial date to a very old time

        for (let ext of possibleExtensions) {
            try {
                const artResponse = await fetch(`art.${ext}?timestamp=${new Date().getTime()}`);
                if (artResponse.ok) {
                    const lastModified = artResponse.headers.get('Last-Modified');
                    if (lastModified) {
                        const modifiedDate = new Date(lastModified);
                        if (modifiedDate > mostRecentDate) {
                            mostRecentDate = modifiedDate;
                            mostRecentArtUrl = `art.${ext}`;
                        }
                    }
                } else {
                    console.warn(`Failed to fetch art.${ext} - status: ${artResponse.status}`);
                }
            } catch (error) {
                console.warn(`Error fetching art.${ext}:`, error);
                // Continue to the next extension if this one fails
            }
        }

        // If no valid art file is found, use a default image
        if (!mostRecentArtUrl) {
            console.warn("No valid album art found, using default.");
            mostRecentArtUrl = "default-art.png";  // Fallback option
        }

        console.log("Parsed Band:", band);
        console.log("Parsed Track:", track);
        console.log("Using Album Art:", mostRecentArtUrl);

        // Update the HTML with the new data
        document.getElementById('song-title').textContent = `Track: ${track}`;
        document.getElementById('song-band').textContent = `Band: ${band}`;
        document.getElementById('album-art').src = mostRecentArtUrl;

        // Update the document's title
        const newTitle = `${band} - ${track}`;
        document.title = newTitle;

        // Update the media session metadata for Android notifications
        if ('mediaSession' in navigator) {
            navigator.mediaSession.metadata = new MediaMetadata({
                title: track,
                artist: band,
                artwork: [
                    { src: mostRecentArtUrl, sizes: '512x512', type: 'image/png' }
                ]
            });
        }

    } catch (error) {
        console.error('Error fetching song data:', error);
    }
}

// Fetch song data every 100 seconds
setInterval(fetchSongData, 100000);

// Initial fetch
fetchSongData();
