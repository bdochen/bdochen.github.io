// 配置
const SOURCE_URL = "http://47.110.243.216:51234/";
const CACHE_12_HOURS = 43200; // 12小时缓存，每天更新2次

export async function onRequest(context) {
  const { request } = context;
  const cache = caches.default;

  // 优先读取缓存
  let cachedResponse = await cache.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }

  try {
    // 抓取直播源，带上Referer和Host头避免拦截
    const res = await fetch(SOURCE_URL, {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "http://47.110.243.216:51234/",
        "Host": "47.110.243.216:51234"
      },
    });

    // 按你需要的响应头返回数据
    const response = new Response(res.body, {
      headers: {
        "Content-Type": "text/plain;charset=UTF-8",
        "Cache-Control": `max-age=${CACHE_12_HOURS}`,
        "Access-Control-Allow-Origin": "*",
        "Connection": "keep-alive",
        "Keep-Alive": "timeout=5"
      },
    });

    // 写入缓存
    context.waitUntil(cache.put(request, response.clone()));
    return response;
  } catch (e) {
    return new Response("获取源失败：" + e.message, { status: 500 });
  }
}
