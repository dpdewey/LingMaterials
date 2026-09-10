/**
 * Netlify Function — AI summary proxy
 * ---------------------------------------------------------------
 * Frontend calls /api/summary with a JSON body { entries: [...] }.
 * This function adds the ANTHROPIC_API_KEY (from environment),
 * calls api.anthropic.com, and returns { text: "..." }.
 *
 * Configure in netlify.toml:
 *   [[redirects]]
 *     from = "/api/summary"
 *     to = "/.netlify/functions/summary"
 *     status = 200
 *
 * Set the secret in Netlify dashboard:
 *   Site settings → Environment variables → ANTHROPIC_API_KEY
 *
 * For Vercel: rename to api/summary.js (works the same — Vercel
 * automatically routes any file under /api/ to a function endpoint).
 *
 * For Cloudflare Workers: the body of the handler is portable;
 * just wrap it in addEventListener('fetch', ...) instead.
 */

exports.handler = async function (event) {
  // CORS preflight
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: corsHeaders(),
      body: ''
    };
  }

  if (event.httpMethod !== 'POST') {
    return jsonResponse(405, { error: 'Method not allowed' });
  }

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return jsonResponse(500, { error: 'Server is missing ANTHROPIC_API_KEY' });
  }

  let payload;
  try {
    payload = JSON.parse(event.body || '{}');
  } catch (e) {
    return jsonResponse(400, { error: 'Invalid JSON' });
  }

  const entries = Array.isArray(payload.entries) ? payload.entries : [];
  if (!entries.length) {
    return jsonResponse(400, { error: 'No entries provided' });
  }

  // Cap input size — defensive
  const MAX_ENTRIES = 100;
  const safeEntries = entries.slice(0, MAX_ENTRIES);

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
      return jsonResponse(502, { error: 'Upstream API error', status: apiResponse.status });
    }

    const data = await apiResponse.json();
    const text = (data.content || [])
      .filter(function (b) { return b.type === 'text'; })
      .map(function (b) { return b.text; })
      .join('')
      .trim();

    if (!text) {
      return jsonResponse(502, { error: 'Empty response from API' });
    }

    return jsonResponse(200, { text: text });
  } catch (err) {
    console.error('Function error:', err);
    return jsonResponse(500, { error: 'Function error: ' + err.message });
  }
};

function corsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
  };
}

function jsonResponse(statusCode, body) {
  return {
    statusCode: statusCode,
    headers: Object.assign(
      { 'Content-Type': 'application/json' },
      corsHeaders()
    ),
    body: JSON.stringify(body)
  };
}
