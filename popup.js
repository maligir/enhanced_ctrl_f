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

    displayResults(results.result);
  });
});

function searchForText(query) {
  const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // Escapes special characters for regex
  const regex = new RegExp('\\b' + escapedQuery + '\\b', 'gi');
  let results = [];
  let words = document.body.innerText.split(' ');

  for (let i = 0; i < words.length; i++) {
    if (regex.test(words[i])) {
      results.push(words.slice(Math.max(i-2, 0), i+3).join(' '));
      regex.lastIndex = 0; // Reset regex state due to global flag
    }
  }

  return results;
}

function displayResults(results) {
  const resultsContainer = document.getElementById('results');
  resultsContainer.innerHTML = '';

  for (let result of results) {
    const p = document.createElement('p');
    p.textContent = result;
    resultsContainer.appendChild(p);
  }
}
