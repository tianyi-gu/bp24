chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "capture") {
    chrome.tabs.captureVisibleTab(null, { format: "png" }, (dataUrl) => {
      sendResponse({ screenshotUrl: dataUrl });
    });
    console.log("took screenshot");
    return true; // Indicates that the response is asynchronous
  }
});
