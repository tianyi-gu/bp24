chrome.action.onClicked.addListener((tab) => {
  chrome.tabs.captureVisibleTab(tab.windowId, {format: 'png'}, (dataUrl) => {
    // Use the chrome.downloads API to download the image
    chrome.downloads.download({
      url: dataUrl,
      filename: 'screenshot.png'
    });
  });
});

function dataURLToBlob(dataUrl) {
  const parts = dataUrl.split(',');
  const mime = parts[0].match(/:(.*?);/)[1];
  const binary = atob(parts[1]);
  const array = [];
  for (let i = 0; i < binary.length; i++) {
    array.push(binary.charCodeAt(i));
  }
  return new Blob([new Uint8Array(array)], {type: mime});
}
