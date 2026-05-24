chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === "install") {
    console.log("Extension installed. Run install.py to set up native messaging.");
  }
});

const api_url = 'https://api.boot.dev/v1/static/';
chrome.action.onClicked.addListener(async (tab) => {
  let parts = tab.url.split('dev');
  let lesson_url = api_url + parts[1];
  let buffers = {};
  try {
    const response = await fetch(lesson_url);
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`);
    }

    const result = await response.json();
    for(const file of result.Lesson.LessonDataCodeTests.StarterFiles){
      buffers[file.Name] = file.Content;
    }
  } catch (error) {
    console.error(error.message);
  }
  
  if (Object.keys(buffers).length > 0) {
    try {
      const result = await chrome.runtime.sendNativeMessage("nvim_bridge", buffers);
    } catch (err) {
      console.error("Native messaging error:", err);
    }
  }
});

const MATCH_PATTERN = /boot\.dev\/lessons\//;
const ACTIVE_ICON = { path: { 32: 'images/icon-active.png' } };
const DEFAULT_ICON = { path: { 32: 'images/icon-inactive.png' } };
function updateIcon(tabId, url) {
  const icon = url && MATCH_PATTERN.test(url) ? ACTIVE_ICON : DEFAULT_ICON;
  chrome.action.setIcon({ tabId, ...icon });
}
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.url) updateIcon(tabId, changeInfo.url);
});
chrome.tabs.onActivated.addListener((activeInfo) => {
  chrome.tabs.get(activeInfo.tabId, (tab) => updateIcon(tab.id, tab.url));
});
