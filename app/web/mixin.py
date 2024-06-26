from aiohttp.abc import StreamResponse

from aiohttp.web_exceptions import HTTPUnauthorized


class AuthRequiredMixin:
    async def _iter(self) -> StreamResponse:
        if not getattr(self.request, "user", None) and self.request.method != "OPTIONS":
            raise HTTPUnauthorized(reason="Ошибка првоерки авторизации")
        return await super(AuthRequiredMixin, self)._iter()
