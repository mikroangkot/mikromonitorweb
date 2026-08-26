import flet as ft
from datetime import datetime, timezone
from app.helpers.dataformatter import DataFormatter
from typing import Callable, Dict


class RouteGuard:
    def __init__(
        self,
        builder: Callable[[ft.Page], ft.View],
        protected: bool = False,
        guest_only: bool = False
    ):
        self.builder = builder
        self.protected = protected
        self.guest_only = guest_only


class Router:
    def __init__(self, page: ft.Page):
        self.page = page
        self.routes: Dict[str, RouteGuard] = {}
        self.page.on_route_change = self._middleware_pipeline
        self.storage = DataFormatter()

    def add_route(
        self,
        path: str,
        builder: Callable[[ft.Page], ft.View],
        protected: bool = False,
        guest_only: bool = False
    ):
        self.routes[path] = RouteGuard(builder, protected, guest_only)

    def _is_token_valid(self, token: str) -> bool:
        if not token:
            return False
        try:
            payload = DataFormatter.decodetoken(token)
            exp = payload.get("exp")
            if not exp:
                return True
            current_time = datetime.now(timezone.utc).timestamp()
            return exp > current_time
        except Exception:
            return False

    async def _middleware_pipeline(self, e: ft.RouteChangeEvent):
        target_route = self.page.route
        token = await self.storage.get("token")
        is_authenticated = self._is_token_valid(token)
        if token and not is_authenticated:
            await self.storage.remove("token")
            await self.storage.remove("current_user")
            page.session.store.remove("current_user")
        server_status = getattr(self.page, "server_status", "open")
        if server_status == "close" and target_route != "/503":
            return await self.page.push_route("/503")
        if target_route not in self.routes:
            target_route = "/404"
        guard = self.routes[target_route]
        if guard.protected and not is_authenticated:
            return await self.page.push_route("/signin")
        if guard.guest_only and is_authenticated:
            return await self.page.push_route("/home")
        self.page.views.clear()
        view = guard.builder(self.page)
        self.page.views.append(view)
        self.page.update()
