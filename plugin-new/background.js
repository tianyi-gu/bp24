console.log("asdnfasdf");
chrome.commands.onCommand.addListener(function (command) {
  if (command === "screenshot") {
    console.log("test");
  }
});
