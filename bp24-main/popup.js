document.addEventListener('DOMContentLoaded', () => {
    const captureBtn = document.getElementById('captureBtn');
    captureBtn.addEventListener('click', () => {
      chrome.runtime.sendMessage({action: 'capture'});
    });
  });
  