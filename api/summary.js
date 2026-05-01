/**
 * Vercel Serverless Function — AI summary proxy
 * Mirror of netlify/functions/summary.js with Vercel's request/response signature.
 *
 * Set ANTHROPIC_API_KEY in Vercel project settings → Environment Variables.
 * Vercel automatically routes any file under /api/ to a function endpoint,
 * so the frontend can call /api/summary without additional configuration.
 */

module.exports = async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    res.status(500).json({ error: 'Server is missing ANTHROPIC_API_KEY' });
    return;
  }

  const payload = req.body || {};
  const entries = Array.isArray(payload.entries) ? payload.entries : [];
  if (!entries.length) {
    res.status(400).json({ error: 'No entries provided' });
    return;
  }

  const safeEntries = entries.slice(0, 100);

  const prompt =
    'You are writing a short editorial synthesis for the BYU Department of Linguistics ' +
    'mentoring archive — a public page documenting how faculty have mentored students across ' +
    'Linguistics, TESOL, and Editing & Publishing.\n\n' +
    'Below are ' + safeEntries.length + ' mentor-submitted entries. Write a single paragraph of ' +
    '3–5 sentences (around 75–115 words) that captures the texture of this body of work: ' +
    'what mentors and students are doing together, what kinds of accomplishments recur, and ' +
    'what feels distinctive. Be specific where you can — name a few projects, themes, or ' +
    'kinds of work. Avoid clichés ("dedicated faculty", "exciting opportunities"). Keep an ' +
    'editorial, slightly literary register that fits a department of linguists, TESOL teachers, ' +
    'and editors. Do not begin with "This archive" or "The archive". Do not use a bulleted list. ' +
    'Write in plain prose only. No quotation marks around your output.\n\n' +
    'ENTRIES (JSON):\n' + JSON.stringify(safeEntries, null, 0);

  try {
    const apiResponse = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 400,
        messages: [{ role: 'user', content: prompt }]
      })
    });

    if (!apiResponse.ok) {
      const errBody = await apiResponse.text();
      console.error('Anthropic API error:', apiResponse.status, errBody);
      res.status(502).json({ error: 'Upstream API error', status: apiResponse.status });
      return;
    }

    const data = await apiResponse.json();
    const text = (data.content || [])
      .filter(function (b) { return b.type === 'text'; })
      .map(function (b) { return b.text; })
      .join('')
      .trim();

    if (!text) {
      res.status(502).json({ error: 'Empty response from API' });
      return;
    }

    res.status(200).json({ text: text });
  } catch (err) {
    console.error('Function error:', err);
    res.status(500).json({ error: 'Function error: ' + err.message });
  }
};
