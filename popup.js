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
  
      // Save the search query and results to storage
      chrome.storage.local.set({
        lastSearchQuery: query,
        lastSearchResults: results.result
      }, function() {
        displayResults(results.result);
      });
    });
  });
  
  function searchForText(query) {
    const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // Escapes special characters for regex
    const regex = new RegExp('\\b' + escapedQuery + '\\b', 'gi');
    let results = [];
    let words = document.body.innerText.split(' ');
  
    for (let i = 0; i < words.length; i++) {
      if (regex.test(words[i])) {
        const surroundingText = words.slice(Math.max(i-2, 0), i+3).join(' ');
        const expandedText = words.slice(Math.max(i-10, 0), i+11).join(' ');  // Grab 10 words before and after the found instance
        results.push({text: surroundingText, expandedText: expandedText});
        regex.lastIndex = 0; // Reset regex state due to global flag
      }
    }
  
    return results;
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