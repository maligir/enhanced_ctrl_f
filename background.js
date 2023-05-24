chrome.action.onClicked.addListener((tab) => {
    chrome.scripting.executeScript({
      target: {tabId: tab.id},
      files: ['content.js']
    });
  });
  
  chrome.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
      if (request.type === "storeData") {
        console.log(request.data);  // In reality, store data here
  
        // Optional: Respond back to the content/popup script
        sendResponse({status: 'Data received and stored'});
      }
    }
  );
  