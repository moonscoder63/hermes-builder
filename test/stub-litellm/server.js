// Минимальный OpenAI-совместимый stub для локального E2E web-chat без реального
// ключа: агент (OPENAI_BASE_URL=http://host.docker.internal:8899/v1) шлёт сюда
// /v1/chat/completions → возвращаем канонический ответ. Логируем запросы.
const http = require("http");
const PORT = process.env.STUB_PORT || 8899;

const server = http.createServer((req, res) => {
  let body = "";
  req.on("data", (c) => (body += c));
  req.on("end", () => {
    const ts = new Date().toISOString();
    console.error(`[stub ${ts}] ${req.method} ${req.url} (${body.length}b)`);
    res.setHeader("Content-Type", "application/json");

    if (req.url.includes("/models")) {
      res.end(JSON.stringify({ object: "list", data: [{ id: "gpt-5-mini", object: "model" }] }));
      return;
    }
    if (req.url.includes("/chat/completions")) {
      // Поддержим и stream, и non-stream — отдадим non-stream (агент обычно ок).
      res.end(
        JSON.stringify({
          id: "chatcmpl-stub",
          object: "chat.completion",
          model: "gpt-5-mini",
          choices: [
            {
              index: 0,
              message: { role: "assistant", content: "STUB_REPLY: привет из stub-LLM" },
              finish_reason: "stop",
            },
          ],
          usage: { prompt_tokens: 5, completion_tokens: 7, total_tokens: 12 },
        })
      );
      return;
    }
    res.statusCode = 404;
    res.end(JSON.stringify({ error: "stub: unknown path" }));
  });
});
server.listen(PORT, "0.0.0.0", () => console.error(`stub-litellm on :${PORT}`));
