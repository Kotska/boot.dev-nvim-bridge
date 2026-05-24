chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getLessonContent") {

    getData();
    // sendResponse(content);
  }
  async function getData(){
    (async () => {
      // see the note below on how to choose currentWindow or lastFocusedWindow
      const [tab] = await chrome.tabs.query({active: true, lastFocusedWindow: true});
      console.log(tab.url);
      // ..........
    })();

    const url = "https://example.org/products.json";
  }
});
