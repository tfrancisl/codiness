async function pollStatus(url, attempts = 3) {
  for (let i = 0; i < attempts; i++) {
    try {
      const res = await fetch(url);
      if (res.ok) return true;
    } catch (err) {
      // ignore and retry
    }
  }
  return false;
}

module.exports = { pollStatus };
