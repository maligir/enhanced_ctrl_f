document.getElementById('darkModeToggle').addEventListener('change', function() {
    document.body.classList.toggle('dark-mode', this.checked);
    // Save the state of dark mode in local storage
    chrome.storage.local.set({ darkModeEnabled: this.checked });
});

window.onload = function() {
    chrome.storage.local.get(['darkModeEnabled', 'lastSearchQuery', 'lastSearchResults'], function(data) {
        if (data.lastSearchQuery && data.lastSearchResults) {
            document.getElementById('searchText').value = data.lastSearchQuery;
            displayResults(data.lastSearchResults);
        }
        const darkModeToggle = document.getElementById('darkModeToggle');
        darkModeToggle.checked = !!data.darkModeEnabled;
        document.body.classList.toggle('dark-mode', darkModeToggle.checked);
    });
}

document.getElementById('searchButton').addEventListener('click', async () => {
    const query = document.getElementById('searchText').value;

    if (!query) {
        alert("Please enter some text to search");
        return;
    }

    let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    chrome.scripting.executeScript({
        target: {tabId: tab.id},
        func: searchForText,
        args: [query]
    }, ([results]) => {
        if (chrome.runtime.lastError) {
            console.error(chrome.runtime.lastError);
            return;
        }
        
        // Check if an error message was returned
        if (results.result.error) {
            displayResults([results.result.error]);
        } else {
            // Save the search query and results to storage
            chrome.storage.local.set({
            lastSearchQuery: query,
            lastSearchResults: results.result
            }, function() {
            displayResults(results.result);
            });
        }
    });
});

async function searchForText(query) {
    const bodyText = document.body.innerText;

    // Check if the page has text content
    if (!bodyText || bodyText.trim() === '') {
        return { error: 'No text content found on this page.' };
    }

    try {
        const response = await fetch('http://127.0.0.1:5000/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                text: bodyText
            }),
        });

        const data = await response.json();

        // Handle the response from the server
        if (data.error) {
            return { error: data.error };
        } else {
            return data.results;
        }
    } catch (error) {
        console.error('Error:', error);
        return { error: 'An error occurred while processing your request.' };
    }
}

let storedResults = [];

function displayResults(results) {
    storedResults = results;  // Store the results to be able to return to them

    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = '';

    for (let i = 0; i < results.length; i++) {
        const result = results[i];
        const p = document.createElement('p');
        p.textContent = result.text;

        p.addEventListener('click', () => {
            // Clear the container and show expanded text for the clicked instance
            resultsContainer.innerHTML = '';
            const expandedP = document.createElement('p');
            expandedP.textContent = result.expandedText;
            resultsContainer.appendChild(expandedP);

            // Add a back button to return to the original results display
            const backButton = document.createElement('button');
            backButton.textContent = 'Back';
            backButton.addEventListener('click', () => displayResults(storedResults));
            resultsContainer.appendChild(backButton);
        });

        resultsContainer.appendChild(p);
    }
}
