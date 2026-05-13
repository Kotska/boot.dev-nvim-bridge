chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === "install") {
    console.log("Extension installed. Run install.py to set up native messaging.");
  }
});

chrome.action.onClicked.addListener(async (tab) => {
  const response = await chrome.tabs.sendMessage(tab.id, { action: "getSelection" });
  
  if (response) {
    try {
      const result = await chrome.runtime.sendNativeMessage("nvim_bridge", response);
      console.log("Sent to Neovim:", result);
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
