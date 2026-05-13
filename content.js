chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getSelection") {
    let textbox = document.querySelectorAll('[role="textbox"]');
    let textboxNames = document.querySelectorAll('li[role="tab"]');
    if (textbox.length == 0 || textboxNames.length == 0) {
      sendResponse(false);
      return true;
    }

    function getText(el) {
      let t = el.innerText;
      if (t.includes('\n')) return t;
      t = el.textContent;
      if (t.includes('\n')) return t;
      let lines = el.querySelectorAll('.cm-line');
      if (lines.length) {
        return Array.from(lines).map(l => l.textContent).join('\n');
      }
      return el.textContent;
    }

    let buffers = {}
    textbox.forEach((e, i) => {
      let bufferName = textboxNames[i].innerText.trim();
      buffers[bufferName] = getText(textbox[i]);
    });
    sendResponse(buffers);
  }
});
