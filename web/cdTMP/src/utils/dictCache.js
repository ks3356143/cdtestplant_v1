/**
 * 字典短缓存：同一字典 code 在 TTL 内只请求一次，并合并并发请求。
 * 字典项被增删改时调用 clearDictCache() 主动失效，避免管理页修改后长时间看到旧数据。
 */
const cache = new Map() // code -> { time, promise }
const DEFAULT_TTL = 60 * 1000

export function getCachedDict(code, fetcher, ttl = DEFAULT_TTL) {
    const now = Date.now()
    const hit = cache.get(code)
    if (hit && now - hit.time < ttl) {
        return hit.promise
    }
    const promise = Promise.resolve()
        .then(fetcher)
        .catch((err) => {
            // 失败不缓存，下次调用重新请求
            cache.delete(code)
            throw err
        })
    cache.set(code, { time: now, promise })
    return promise
}

export function clearDictCache(code) {
    if (code) {
        cache.delete(code)
    } else {
        cache.clear()
    }
}
