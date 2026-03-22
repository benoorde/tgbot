/**
 * Cloudflare Worker для Telegram бота.
 * Пересылает входящие Webhook-запросы на ваш Python-сервер.
 */

// ВАЖНО: Укажите здесь IP вашего сервера, где запущен бот.
// Ссылка api.telegram.org... НЕ ПОДХОДИТ (это ссылка регистрации, а не приема сигналов).
// Пример: "http://45.132.12.11:8080/webhook"
const BACKEND_URL = "http://YOUR_VPS_IP:8080/webhook";

// Секретный токен для защиты (должен совпадать с тем, что вы установите в боте)
const SECRET_TOKEN = ""; 

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url);

  // Обрабатываем только POST запросы (апдейты от Telegram)
  if (request.method === "POST") {
    // Создаем новый запрос к вашему Python-серверу
    const newRequest = new Request(BACKEND_URL, {
      method: request.method,
      headers: request.headers,
      body: request.body
    });

    try {
      // Пересылаем запрос и возвращаем ответ от бота
      const response = await fetch(newRequest);
      return response;
    } catch (e) {
      return new Response(`Error connecting to backend: ${e.message}`, { status: 502 });
    }
  }

  // Ответ для проверки работоспособности воркера
  return new Response("Telegram Worker Proxy is running.", { status: 200 });
}