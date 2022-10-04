import asyncio
import json
from playwright.async_api import Page, Error, Browser, Playwright,BrowserContext, async_playwright,WebSocket
from typing import Optional
import os
import sys
import playwright.__main__

class web_browser:
    def __init__(self,default_cookie_path:str=None) -> None:
        self.__driver :Optional[Playwright]= None
        self.__browser:Optional[Browser]= None
        self.__context:Optional[BrowserContext] = None
        self.default_browser = "firefox"
        self.logger_func = print
        self.headless = True
        self.default_cookie_path = default_cookie_path
        self.websocket:WebSocket.on("framereceived")
        pass

    
    async def init_browser(self,**kwargs):
        self.__driver = await async_playwright().start()
        try:
            self.__browser = await self.launch_browser(**kwargs)
        except Error:
            await self.install_browser()
            self.__browser = await self.launch_browser(**kwargs)
        try:
            self.__context = await self.get_context()
            await self.__context.clear_permissions() 
        except Exception as e:
            self.logger(e)
            while True:
                pass
        return

    async def launch_browser(self,**kwargs) -> Browser:
        if self.__driver is None:
            self.logger_func("e","Playwright is not initialized")
            return None
        if self.default_browser == "firefox":
            await self.logger("启动Firefox中....")
            return await self.__driver.firefox.launch(headless=self.headless,firefox_user_prefs={"media.autoplay.block-event.enabled":True,"media.autoplay.block-webaudio":True,"media.autoplay.default":5},**kwargs)

        else:
            await self.logger("使用 chromium 启动")
            return await self.__driver.chromium.launch(headless=self.headless,**kwargs)

    async def shutdown_browser(self):
        if self.__context:
            await self.__context.close()
        if self.__browser:
            await self.__browser.close()
        if self.__driver:
            await self.__driver.stop()
        return 


    async def install_browser(self):
        if self.default_browser == "firefox":
            await self.info("正在安装 firefox")
            sys.argv = ["", "install", "firefox"]
        else:
            await self.info("正在安装 chromium")
            sys.argv = ["", "install", "chromium"]
        try:
            await self.logger("正在安装依赖")
            os.system("playwright install-deps")
            playwright.__main__.main()
        except SystemExit:
            pass
        return

    async def get_browser(self):
        return self.__browser

    async def get_context(self,cookie_path:str=None,**kwargs)->BrowserContext:
        if cookie_path is None:
            cookie_path = self.default_cookie_path
        return await self.__browser.new_context(java_script_enabled=True,storage_state=cookie_path,**kwargs)
    
    async def get_page(self,**kwargs) -> Page:
        return await self.__context.new_page(**kwargs)

    async def get_storage_state(self):
        return await self.__context.storage_state()

    async def open_page(self,page:Page,url:str,**kwargs):
        try:
            await page.goto(url=url,timeout=0,**kwargs)
        except Exception as e:
            self.logger(e)
        return

    async def close_page(self,page:Page):
        if page is not None:
            await page.close()
        return

    async def logger(self,info):
        self.logger_func(info)
        return

