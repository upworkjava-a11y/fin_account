(function () {
  const statusEl = document.getElementById('eriStatus');
  const keysEl = document.getElementById('eriKeys');
  const errorEl = document.getElementById('eriError');
  if (!statusEl) return;

  const copy = JSON.parse(document.getElementById('eri-copy').textContent);
  const apiKeys = JSON.parse(document.getElementById('eri-api-keys').textContent);
  const wsUrl = JSON.parse(document.getElementById('eri-ws').textContent);
  const csrf = (document.cookie.match(/(?:^|; )csrftoken=([^;]+)/) || [])[1] || '';

  let socket;
  let seq = 0;
  const pending = new Map();

  function showError(text) {
    errorEl.hidden = false;
    errorEl.textContent = text;
    statusEl.hidden = true;
  }

  function messageFor(code) {
    return copy.errors[code] || code;
  }

  function call(payload) {
    return new Promise((resolve, reject) => {
      const id = ++seq;
      pending.set(id, { resolve, reject });
      socket.send(JSON.stringify(Object.assign({ cbid: id }, payload)));
      setTimeout(() => {
        if (pending.has(id)) {
          pending.delete(id);
          reject(new Error('timeout'));
        }
      }, 60000);
    });
  }

  function onMessage(event) {
    let data;
    try { data = JSON.parse(event.data); } catch (err) { return; }
    const id = data.cbid || data.id;
    const waiter = pending.get(id);
    if (!waiter) return;
    pending.delete(id);
    if (data.success === false) waiter.reject(new Error(data.reason || 'eimzo'));
    else waiter.resolve(data);
  }

  function parseAlias(alias) {
    const out = {};
    String(alias || '').split(',').forEach((part) => {
      const index = part.indexOf('=');
      if (index > 0) out[part.slice(0, index).trim().toLowerCase()] = part.slice(index + 1).trim();
    });
    return out;
  }

  function certificatesOf(data) {
    const list = data.certificates || (data.result && data.result.certificates) || data.result || [];
    return Array.isArray(list) ? list : Object.values(list);
  }

  async function sign(item) {
    statusEl.hidden = false;
    statusEl.textContent = copy.wait;
    errorEl.hidden = true;
    const loaded = await call({
      plugin: 'pfx',
      name: 'load_key',
      arguments: [item.disk, item.path, item.name, item.alias],
    });
    const keyId = loaded.keyId || (loaded.result && loaded.result.keyId);
    const challengeResponse = await fetch('/eri/challenge/', { credentials: 'same-origin' });
    const challengeBody = await challengeResponse.json();
    if (!challengeBody.ok) throw new Error(messageFor(challengeBody.error));
    const data = btoa(unescape(encodeURIComponent(challengeBody.challenge)));
    const signed = await call({
      plugin: 'pkcs7',
      name: 'create_pkcs7',
      arguments: [data, keyId, 'no'],
    });
    const pkcs7 = signed.pkcs7_64 || (signed.result && signed.result.pkcs7_64);
    const verified = await fetch('/eri/verify/', {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': decodeURIComponent(csrf) },
      body: JSON.stringify({ pkcs7: pkcs7 }),
    });
    const body = await verified.json();
    if (!body.ok) throw new Error(messageFor(body.error));
    window.location.href = body.redirect || '/app/';
  }

  function render(list) {
    keysEl.innerHTML = '';
    if (!list.length) {
      showError(copy.missing);
      return;
    }
    statusEl.textContent = copy.pick;
    list.forEach((item) => {
      const alias = parseAlias(item.alias);
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'key-btn';
      const title = document.createElement('strong');
      title.textContent = alias.cn || item.name || 'ERI';
      const meta = document.createElement('span');
      meta.textContent = alias.tin || alias.serialnumber || alias.uid || '';
      button.append(title, meta);
      button.addEventListener('click', () => {
        sign(item).catch((err) => showError(err.message || copy.missing));
      });
      keysEl.appendChild(button);
    });
    keysEl.hidden = false;
  }

  function start() {
    socket = new WebSocket(wsUrl);
    socket.onmessage = onMessage;
    socket.onerror = () => showError(copy.missing);
    socket.onclose = () => {
      if (keysEl.hidden) showError(copy.missing);
    };
    socket.onopen = async () => {
      try {
        await call({ name: 'apikey', arguments: apiKeys });
        const listed = await call({ plugin: 'pfx', name: 'list_all_certificates', arguments: [''] });
        render(certificatesOf(listed));
      } catch (err) {
        showError(copy.missing);
      }
    };
  }

  start();
})();
