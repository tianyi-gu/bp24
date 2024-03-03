chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "capture") {
    chrome.tabs.captureVisibleTab(null, { format: "png" }, (dataUrl) => {
      chrome.tabs.sendMessage(sender.tab.id, { screenshotUrl: dataUrl });
      sendResponse({ screenshotUrl: dataUrl });
    });
    return true; // Indicates that the response is asynchronous
  }
});
