document.addEventListener('DOMContentLoaded', () => {
    const captureBtn = document.getElementById('captureBtn');
    const screenshotImg = document.getElementById('screenshotImg');
  
    captureBtn.addEventListener('click', () => {
      chrome.runtime.sendMessage({action: 'capture'}, (response) => {
        screenshotImg.src = response.screenshotUrl;
      });
    });
  });
  