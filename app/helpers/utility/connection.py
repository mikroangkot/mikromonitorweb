import flet as ft
import asyncio
import inspect

class Connectivity:

    def __init__(self, page: ft.Page, on_change=None):
        self.page = page
        self.on_change = on_change
        self.connectivity = ft.Connectivity()
        self.connectivity.on_change = self._handle_change
        self.page.run_task(self._check_initial_status)

    async def _check_initial_status(self):
        try:
            await asyncio.sleep(0.1)
            current_connectivity = await self.connectivity.get_connectivity()
            await self._process_status(current_connectivity)
        except Exception:
            pass

    async def _handle_change(self, e: ft.ConnectivityChangeEvent):
        await self._process_status(e.connectivity)

    async def _process_status(self, connectivity_list):
        is_online = ft.ConnectivityType.NONE not in connectivity_list
        if self.on_change:
            if inspect.iscoroutinefunction(self.on_change):
                await self.on_change(is_online, connectivity_list)
            else:
                self.on_change(is_online, connectivity_list)
        try:
            self.page.update()
        except Exception:
            pass