document.addEventListener("DOMContentLoaded", () => {
  const scrapeBtn = document.getElementById("scrapeBtn");
  const resultsDiv = document.getElementById("results");
  //   const captureBtn = document.getElementById("captureBtn");

  //   captureBtn.addEventListener("click", () => {
  //     chrome.runtime.sendMessage({ action: "capture" });
  //   });
  scrapeBtn.addEventListener("click", () => {
    fetch("http://localhost:8000/image", {
      method: "POST",
      mode: "cors",
      body: new FormData(document.getElementById("imageForm")),
    })
      //     ;
      // // Your fetch call to the backend service
      // fetch("http://localhost:3000/scrape", {
      //   method: "POST",
      //   headers: {
      //     "Content-Type": "application/json",
      //   },
      //   body: JSON.stringify({
      //     categoryOrProductUrls: [
      //       {
      //         url: "https://www.amazon.com/s?k=black+shirts&ref=nb_sb_noss",
      //       },
      //     ],
      //     maxItemsPerStartUrl: 5,
      //     useCaptchaSolver: false,
      //     scrapeProductVariantPrices: false,
      //     proxyConfiguration: {
      //       useApifyProxy: true,
      //       apifyProxyGroups: ["RESIDENTIAL"],
      //     },
      //   }),
      // })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        // data = JSON.parse(data);
        console.log(data);
        // Clear previous results
        resultsDiv.innerHTML = "";
        resultsDiv.style.display = "flex";
        resultsDiv.style.zIndex = 20; // results is always on top now
        // generate HTML for each item and append to resultsDiv
        data["amazon"]["items"].forEach((item) => {
          const itemDiv = document.createElement("div");
          itemDiv.className = "item";

          const title = document.createElement("h3");
          title.textContent = item.title;
          title.href = item.url;

          // const link = document.createElement('a'); / hyperlinked to text now
          // link.textContent = 'View on Amazon';
          // link.target = '_blank';

          const image = document.createElement("img");
          image.src = item.thumbnailImage;
          image.alt = item.title;

          itemDiv.appendChild(image);
          itemDiv.appendChild(title);
          // itemDiv.appendChild(link);

          resultsDiv.appendChild(itemDiv);
        });
      })
      .catch((error) => {
        resultsDiv.textContent = `Error: ${error}`;
      });
  });
});
