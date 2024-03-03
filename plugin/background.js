chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log("hi");
  if (request.action === "capture") {
    chrome.tabs.captureVisibleTab(null, { format: "png" }, (dataUrl) => {
      console.log("took screenshot 1");
      chrome.tabs.sendMessage(sender.tab.id, { screenshotUrl: dataUrl });
      sendResponse({ screenshotUrl: dataUrl });
      console.log("took screenshot 2");
    });
    console.log("took screenshot");
    return true; // Indicates that the response is asynchronous
  }
});
