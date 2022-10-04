import os
from pathlib import Path
import random
import re
import sys
import ujson as json
import httpx
import asyncio
import time
import brotli
import threading
from requests_toolbelt.multipart.encoder import MultipartEncoder
from browser import web_browser
from pyfiglet import *
from terminal_layout.extensions.choice import *
from terminal_layout.extensions.input import *
from terminal_layout import *
import tempfile
import platform

if platform.system() == "Windows":
    import win32api,win32con

class RedPacket:
    def __init__(self) -> None:
        self.run_getRedPacketList = []
        self.run_getRedPacketIDList = {}
        self.run_getRedPacketTimeClearList={}
        self.user_cookies_file_path = "./bilibili_cookies.json"
        self.user_playwright_state_file_path = "./bilibili_cookies_playwright.json"
        self.user_self_data = None
        self.join_redpacketlist={}
        self.redPacketPriceLimit = 0
        self.IgnoreRedPacketPrice = []
        self.has_redPacketRoomInfoList = []
        self.run_sendCommitList=[]
        self.debug_display = False
        self.browser_headless = True
        self.living_zone_id = {
            "网游":[2,0],
            "手游":[3,0],
            "单机游戏":[6,0],
            "娱乐":[1,0],
            "电台":[5,0],
            "虚拟主播":[9,0],
            "生活":[10,0],
            "学习":[11,0],
            "赛事":[13,0]
        }
        self.sort_type = {
            "数量优先":True,
            "速度优先":False
        }
        self.task_max_num  =  4
        self.frist_search = True
        self.web_driver = None

        self.async_client = httpx.AsyncClient(timeout=30)
        self.red_packet_max_stop = False 
        self.protect_user_script = "Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});"
        #------------------------红包 web api————————————————————————————————————#
        
        self.web_header = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
            "Accept":"*/*",
            "Accept-Language":"zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding":"gzip",
            "Origin":"https://live.bilibili.com",
            "Connection":"keep-alive, Upgrade",
            "Pragma":"no-cache",
            "Cache-Control":"no-cache",
        }
        self.popularity_red_pocket_info_api = "https://api.live.bilibili.com/xlive/lottery-interface/v1/lottery/getLotteryInfoWeb?roomid={room_id}"
        self.target_user_detail_api = "https://api.bilibili.com/x/space/acc/info?mid={uid}&jsonp=jsonp"
        self.unfollow_user_api = "https://api.bilibili.com/x/relation/modify"
        self.redpackerdraw_api ="https://api.live.bilibili.com/xlive/lottery-interface/v1/popularityRedPocket/RedPocketDraw" 
        self.room_detail_api="https://api.live.bilibili.com/xlive/web-interface/v1/second/getList?platform=web&parent_area_id={parent_zone_id}&area_id={zone_id}&page={page_index}"
        self.room_send_commit_api = "https://api.live.bilibili.com/msg/send"
        self.user_send_session_list_api="https://api.vc.bilibili.com/session_svr/v1/session_svr/get_sessions?session_type=1&group_fold=1&unfollow_fold=0&sort_rule=2&build=0&mobi_app=web"
        self.remove_session_api = "https://api.vc.bilibili.com/session_svr/v1/session_svr/remove_session"
        self.android_header = {
            "User-Agent": "Mozilla/5.0 BiliDroid/6.79.0 (bbcallen@gmail.com) os/android model/Redmi K30 Pro mobi_app/android build/6790300 channel/360 innerVer/6790310 osVer/11 network/2",
            "Accept":"*/*",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Connection": "keep-alive",
            "Accept-Encoding": "gzip, deflate"
        }

        self.face_command_list = ["official_150","official_103","official_115","official_135","official_128"]


    def init_data(self):
        self.logger_info("i","正在启动".center(12,"-"))
        self.logger_info("i"," 信じる心がninnikuuの魔法です！".center(30,"✧"))
        time.sleep(20)
        if not os.path.exists(self.user_cookies_file_path) or not os.path.exists(self.user_playwright_state_file_path):
            self.logger_info("i","未找到账号信息！请登陆！")
            asyncio.run(self.GetAccountAuth())
        try:
            self.user_self_data = self.__load_user_data(self.user_cookies_file_path)
            self.web_driver = web_browser(self.user_playwright_state_file_path)
            self.web_driver.headless = self.browser_headless
            self.web_driver.logger_func=lambda info: self.logger_info("i",info)
            self.bili_jct = self.user_self_data["bili_jct"]
            self.user_self_id = int(self.user_self_data["DedeUserID"])
        except Exception as e:
            os.remove(self.user_cookies_file_path)
            os.remove(self.user_playwright_state_file_path)
            self.logger_info("e","读取账号文件出错！请重新启动程序！")
            time.sleep(120)
            os._exit(0)
        return

    def __load_user_data(self,path):
        if os.path.exists(path):
            with open(path,"r") as f:
                data = f.readlines()
            data = json.loads("".join(data))
            return data
        else:
            self.logger_info("e","No Cookie File!")
            return {}

    
    def __create_user_info(self,room_id,uid,lot_id):
        formData = {}
        formData["lot_id"] = f"{lot_id}"
        formData["csrf_token"]=self.bili_jct
        formData["csrf"]=self.bili_jct
        formData["statistics"]="{'appId':1,'platform':3,'version':'6.79.0','abtest':''}"
        formData["version"]="6.79.0"
        formData["platform"]="android"
        formData["mobi_app"]="android"
        formData["device"]="android"
        formData["channel"]="360"
        formData["c_locale"]="en_US"
        formData["build"]="6790300"
        formData["spm_id"]="444.8.red_envelope.extract"
        formData["ruid"]=f"{uid}"
        formData["room_id"]=f"{room_id}"
        formData["session_id"]=""
        formData["jump_from"]="26000"
        formData["visit_id"]=""
        return formData

    def Run_AsyncTasks(self,tasks):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(*tasks)
        return loop
    
    async def network_get(self,url,header=None):
        if header is None:
            header = self.web_header 
        try:
            recv_data = await self.async_client.get(url,cookies=self.user_self_data,headers=header)
            if recv_data.status_code!=200:
                self.logger_info("e",f"Network Error! API:{url},status code:{recv_data.status_code}")
                return None
        except Exception as e:
            self.logger_info("e",f"Network Error! API:{url},Res:{e}")
            return None
        return recv_data

    async def network_post(self,url,data,header,cookies=True,content=None,files=None):
        try:
            if cookies == False:
                recv_data = await self.async_client.post(url,data=data,headers=header,content=content,files=files)
            else:
                recv_data = await self.async_client.post(url,data=data,headers=header,cookies=self.user_self_data,content=content)
            if recv_data.status_code!=200:
                self.logger_info("e",f"Network Error! API:{url},status code:{recv_data.status_code}")
                return None
        except Exception as e:
            self.logger_info("e",f"Network Error! API:{url},Res:{e}")
            return None
        return recv_data

    async def __HandleRecTextData(self,data,room_id):
        if not room_id in self.run_getRedPacketIDList:
            return
        if not isinstance(data,bytes):
            return
        # 获取数据包的长度，版本和操作类型
        packetLen = int(data[:4].hex(),16)
        ver = int(data[6:8].hex(),16)
        op = int(data[8:12].hex(),16)

        # 有的时候可能会两个数据包连在一起发过来，所以利用前面的数据包长度判断，

        if(len(data)>packetLen):
            await self.__HandleRecTextData(data[packetLen:],room_id)
            data=data[:packetLen]

        # 有时会发送过来 zlib 压缩的数据包，这个时候要去解压。

        if(ver == 2 or ver ==3):
            unzip_data = brotli.decompress(data[16:])
            await self.__HandleRecTextData(unzip_data,room_id)
            return
        
        # ver 不为2也不为1目前就只能是0了，也就是普通的 json 数据。

        # op 为5意味着这是通知消息，cmd 基本就那几个了。
        if(op==5):
            json_info = json.loads(data[16:].decode('utf-8', errors='ignore'))
            if json_info is None:
                return
            if re.findall(str(self.user_self_id),data[16:].decode('utf-8', errors='ignore')):
                self.logger_info("d",f"websocket winner get:{room_id}")
            if(json_info["cmd"]=="POPULARITY_RED_POCKET_WINNER_LIST"):
                self.logger_info("d",f"websocket winners list recv success:{room_id}")
                winners = json_info["data"]["winner_info"]
                lot_id = json_info["data"]["lot_id"]
                if lot_id != self.run_getRedPacketIDList[room_id]:
                    self.run_getRedPacketIDList[room_id] = None
                    return
                get_gift = False
                for winner in winners:
                    if int(winner[0]) == int(self.user_self_id):
                        if not f"{room_id}" in self.join_redpacketlist:
                            self.join_redpacketlist[f"{room_id}"]={"room_id":room_id,"get":True,"gift_info":json_info["data"]["awards"][str(winner[-1])],"total_num":json_info["data"]["total_num"],"winner_num":len(winners)}
                        else:
                            self.join_redpacketlist[f"{room_id}"]["get"] = True
                            self.join_redpacketlist[f"{room_id}"]["gift_info"]=json_info["data"]["awards"][str(winner[-1])]
                            self.join_redpacketlist[f"{room_id}"]["total_num"]=json_info["data"]["total_num"]
                            self.join_redpacketlist[f"{room_id}"]["winner_num"]=len(winners)
                        get_gift = True
                        break
                if not get_gift:
                    if not f"{room_id}" in self.join_redpacketlist:
                        self.join_redpacketlist[f"{room_id}"]={"room_id":room_id,"get":False,"gift_info":None,"total_num":json_info["data"]["total_num"],"winner_num":len(winners)}
                    else:
                        self.join_redpacketlist[f"{room_id}"]["get"] = False
                        self.join_redpacketlist[f"{room_id}"]["gift_info"]=None
                        self.join_redpacketlist[f"{room_id}"]["total_num"]=json_info["data"]["total_num"]
                        self.join_redpacketlist[f"{room_id}"]["winner_num"]=len(winners)
                self.run_getRedPacketIDList[room_id] = None
        elif (op==8):
            pass
        return

    async def room_red_packet_info_get(self,target_rid):
        recv_data = await self.network_get(self.popularity_red_pocket_info_api.format(room_id=target_rid))
        if not recv_data:
            self.logger_info("e",f"Network Error! API:{self.popularity_red_pocket_info_api.format(room_id=target_rid)},Res:No Recv")
            return None
        json_data = json.loads(recv_data.content.decode("utf-8"))
        if json_data["code"]!=0:
            self.logger_info("e",f"Network Error! API:{self.popularity_red_pocket_info_api.format(room_id=target_rid)},message:{json_data['message']}")
            return None
        popularity_red_pocket_info = json_data["data"]["popularity_red_pocket"]
        return popularity_red_pocket_info
    
    async def follow_state_get(self,target_uid):
        recv_data = await self.network_get(self.target_user_detail_api.format(uid=target_uid))
        if not recv_data:
            self.logger_info("e",f"Network Error! API:{self.target_user_detail_api.format(uid=target_uid)},Res:No Recv")
            return False
        json_data = json.loads(recv_data.content.decode("utf-8"))
        if json_data["code"]!=0:
            self.logger_info("e",f"Network Error! API:{self.target_user_detail_api.format(uid=target_uid)},message:{json_data['message']}")
            return False
        return json_data["data"]["is_followed"]
    
    async def drawRedPacketToLimitHandle(self):
        self.red_packet_max_stop = True
        self.logger_info("e","\033[0;31;40m 抢红包次数已达今日上限！已停止！[0m")
        while True:
            await self.web_driver.shutdown_browser()
            loop = asyncio.get_event_loop()
            loop.close()
            time.sleep(120)
            os._exit(0)

    async def drawRedPacket(self,target_rid,target_uid,lot_id):
        user_data = self.__create_user_info(target_rid,target_uid,lot_id)
        formdata = MultipartEncoder(fields=user_data,boundary="---------------------------"+str(random.randint(1e28,1e29-1)))
        self.android_header["Content-Type"] = "multipart/form-data; boundary="+formdata.boundary_value
        recv_data = await self.network_post(self.redpackerdraw_api,formdata.to_string(),self.android_header,cookies=True,content=None,files=None)
        if not recv_data:
            self.logger_info("e",f"Network Error! API:{self.redpackerdraw_api},Res:No Recv")
            return -1,"网络错误！"
        json_data = json.loads(recv_data.content.decode("utf-8"))
        status_code = json_data["code"]
        if re.findall("今日抽奖上限",json_data["message"]):
            await self.drawRedPacketToLimitHandle()
        if re.findall("未登陆",json_data["message"]):
            os.remove(self.user_cookies_file_path)
            os.remove(self.user_playwright_state_file_path)
            self.logger_info("e","账号信息过期,请重新启动程序！")
            time.sleep(120)
            await self.web_driver.shutdown_browser()
            os._exit(0)
        if status_code == 1009109:
            return -1,json_data["message"]
        elif status_code == 1009114:
            return 0,"重复参加"
        elif status_code == 1009106:
            return -2,"重试"
        elif status_code == 0:
            if json_data["data"]["join_status"]==1:
                return 1,"参加成功"
        return -3,json_data["message"]

    async def Entry_Living_Room(self,room_id):
        page = await self.web_driver.get_page()
        await page.add_init_script(self.protect_user_script)
        await self.web_driver.open_page(page,url="https://live.bilibili.com/{}".format(room_id))
        await self.Link_Websocket_Hook(page,room_id=room_id)
        return page

    async def Link_Websocket_Hook(self,page,room_id):
        page.on("websocket",lambda websocket:self.on_websocket_get(websocket,room_id))
        return

    async def Leave_Living_Room(self,page):
        await self.web_driver.close_page(page)
        return

    async def on_websocket_get(self,websocket,room_id):
        websocket.on("framereceived",lambda websocket_data: self.on_websocket_received(websocket_data,room_id))
        
    async def on_websocket_received(self,data,room_id):
        await self.__HandleRecTextData(data,room_id)
        return


    def Commit_CreateBoundary(self):
        start = "---------------------------"
        num = ""
        for i in range(0,29):
            num += str(random.randint(0,9))
        return start+num
    
    def Commit_Createrand(self):
        num = ""
        for i in range(0,10):
            num += str(random.randint(0,9))
        return num

    def Commit_ValueCreate(self,msg,face_mode,room_id):
        mode = "{}".format(1 if face_mode else 0)
        rand_num = self.Commit_Createrand()
        value = {
        "bubble":"0",
        "msg":msg,
        "color":"5566168",
        "mode":"1",
        "fontsize":"25",
        "rnd":rand_num,
        "roomid":str(room_id),
        "dm_type":mode,
        "csrf_token":self.bili_jct,
        "csrf":self.bili_jct,
        }
        boundry = self.Commit_CreateBoundary()
        data = MultipartEncoder(value,boundary=boundry)
        living_room_url =  f"https://live.bilibili.com/{room_id}"
        client_header = {
            "Host": "api.live.bilibili.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer":living_room_url,
            "Content-Type": "multipart/form-data;boundary="+data.boundary_value,
            "Origin": "https://live.bilibili.com",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "TE": "trailers"
        }
        return data.to_string(),client_header
    
    def Commit_SendRequestHandle(self,url,header,data):
        try:
            data = self.sync_network_post(url,data,header)
        except Exception as e:
            self.logger_info("e",e)
            return -1,str(e)
        try:
            data = json.loads(data.content.decode("utf-8"))
        except Exception as e:
            return -1,str(e)
        return data["code"],data["message"]

    def Commit_Send(self,msg,face_mode,room_id):
        send_data,client_header = self.Commit_ValueCreate(msg,face_mode,room_id)
        if not send_data:
            return -1,client_header
        status_code,status_message = self.Commit_SendRequestHandle(self.room_send_commit_api,client_header,send_data)
        return status_code,status_message

    def Commit_Send_Run(self,room_id):
        while room_id in self.run_getRedPacketList:
            msg = random.choice(self.face_command_list)
            state,message = self.Commit_Send(msg,True,room_id)
            self.logger_info("d","弹幕发送,状态码:{},API消息:{}".format(state,message))
            time.sleep(random.randint(20,50))

    def Lanuch_Commit_Send_Thread(self,room_id):
        thread = threading.Thread(target=self.Commit_Send_Run,args=(room_id,),daemon=True)
        thread.start()

    async def RunDrawRedPacket(self,room_id,uid,lot_id):
        join_state,message = await self.drawRedPacket(room_id,uid,lot_id)
        if join_state == 0 or join_state == 1:
            if join_state == 1:
                join_state,message = await self.drawRedPacket(room_id,uid,lot_id)
        elif join_state == -2:
            join_state,message = await self.drawRedPacket(room_id,uid,lot_id)
            if join_state < 0:
                self.run_getRedPacketIDList[room_id]=None
                return False
        else:
            self.run_getRedPacketIDList[room_id]=None
            self.logger_info("e",f"红包API出错:{message}")
            return False
        while self.run_getRedPacketIDList[room_id] is not None:
            if (int(self.run_getRedPacketTimeClearList[room_id]["end_time"])+30) <= int(time.time()):
                break
            await asyncio.sleep(5)
        return True
    

    async def get_talker_id(self,uid):
        data = await self.network_get(self.user_send_session_list_api)
        if data is None:
            self.logger_info("e",f"Network Error! API:{self.user_send_session_list_api},Res:No Recv!")
            return None
        try:
            json_data=json.loads(data.content.decode("utf-8"))
        except Exception as e:
            self.logger_info("e",f"Network Error! API:{self.user_send_session_list_api},Res:Json Decoder Error!")
            return None
        if json_data["code"]!=0:
            self.logger_info("e",f"获取私信会话列表失败:{json_data['messgae']}")
            return None
        if json_data["data"] is None:
            self.logger_info("e",f"获取私信会话列表失败:消息列表为空！")
            return None
        if json_data["data"]["session_list"] is None:
            self.logger_info("e",f"获取私信会话列表失败:消息列表为空！")
            return None
        for session in json_data["data"]["session_list"]:
            sender_uid = int(session["last_msg"]["sender_uid"])
            if uid == sender_uid:
                return session["talker_id"]
        return None

    async def remove_session(self,room_id,uid):
        talker_id = await self.get_talker_id(uid)
        if talker_id is None:
            return False
        remove_data = {
            "talker_id":str(talker_id),
            "session_type":"1",
            "build":"0",
            "mobi_app":"web",
            "csrf_token":self.bili_jct,
            "csrf":self.bili_jct
        }
        data = await self.network_post(self.remove_session_api,data=remove_data,header=self.web_header)
        if data is None:
            self.logger_info("e",f"Network Error! API:{self.remove_session_api},Res:No Recv!")
            return False
        try:
            json_data=json.loads(data.content.decode("utf-8"))
        except Exception as e:
            self.logger_info("e",f"Network Error! API:{self.remove_session_api},Res:Json Decoder Error!")
            return False
        if json_data["message"] == str(json_data["code"]):
            return True
        self.logger_info("d","自动删除会话失败,{}".format(json_data["message"]))
        return False
    
    async def AutoDrawRedPacket(self,room_id,uid):
        room_id = int(room_id)
        if room_id > 0:
            is_follow = await self.follow_state_get(uid)
            if is_follow:
                auto_unfollow = False
            else:
                auto_unfollow = True
            packet_count = 1
            timeout_count = 0
            last_packet_id  = 0
            living_room_page = None
            jump_over_packet_id = 0
            while True:
                packet_info = await self.room_red_packet_info_get(room_id)
                if packet_info is not None:
                    error_count = 0
                    while last_packet_id == packet_info[0]["lot_id"]:
                        packet_info = await self.room_red_packet_info_get(room_id)
                        if packet_info is None:
                            break
                        await asyncio.sleep(5)
                        error_count+=1
                        if error_count>=3:
                            if packet_info is not None:
                                if len(packet_info)>=2:
                                    packet_info.remove(packet_info[0])
                                else:
                                    packet_info = None
                            break
                    last_packet_id = packet_info[0]["lot_id"] if packet_info is not None and len(packet_info)>0 else -1
                packet_price = 0
                if packet_info is not None:
                    packet_price = int(packet_info[0]["total_price"] / 100)
                else: 
                    packet_price = 0

                if packet_info is not None and packet_price !=0:
                    if packet_price in self.IgnoreRedPacketPrice or self.redPacketPriceLimit>=packet_price:
                        if jump_over_packet_id != packet_info[0]["lot_id"]:
                            jump_over_packet_id = packet_info[0]["lot_id"]
                            self.logger_info("w","当前房间[{}],价值:{}电池的红包已被忽略,剩余红包数:{}".format(room_id,packet_price,packet_info[0]["wait_num"]))
                        if packet_info[0]["wait_num"] == 0:
                            break
                        else:
                            packet_info = None
                        await asyncio.sleep(30)
                        continue
                if packet_info is not None:
                    wait_num = packet_info[0]['wait_num']
                    lot_id=packet_info[0]["lot_id"]
                    if room_id not in self.run_getRedPacketTimeClearList:
                        self.run_getRedPacketTimeClearList[room_id]={"end_time":packet_info[0]["end_time"]}
                    else:
                        self.run_getRedPacketTimeClearList[room_id]["end_time"] = packet_info[0]["end_time"]
                    self.run_getRedPacketIDList[room_id]=lot_id
                    if not room_id in self.run_getRedPacketList:
                        self.run_getRedPacketList.append(room_id)
                    if living_room_page is None:
                        living_room_page = await self.Entry_Living_Room(room_id)
                    if not room_id in self.run_sendCommitList:
                        self.run_sendCommitList.append(room_id)
                        self.Lanuch_Commit_Send_Thread(room_id)
                    self.logger_info("i",f"正在毛[{room_id}]直播间的第{packet_count}个红包,红包价值:{packet_price},该直播间还剩{wait_num}个红包")
                    state = await self.RunDrawRedPacket(room_id=room_id,uid=uid,lot_id=lot_id)
                    if not state:
                        self.logger_info("e",f"毛[{room_id}]直播间的第{packet_count}个红包出错")
                    if state:
                        if f"{room_id}" in self.join_redpacketlist:
                            is_get_gift = self.join_redpacketlist[f"{room_id}"]["get"]
                            gift_num = self.join_redpacketlist[f"{room_id}"]["total_num"]
                            awards_user_num = self.join_redpacketlist[f"{room_id}"]["winner_num"]
                            if not is_get_gift:
                                self.logger_info("i",f"[{room_id}]直播间未毛到礼物,红包总数:{gift_num},获奖人数:{awards_user_num}")
                            else:
                                self.logger_info("i","[{}]直播间毛到礼物:[\033[0;32;40m{}\033[0m],红包总数:{},获奖人数:{}".format(room_id,self.join_redpacketlist[f"{room_id}"]["gift_info"]["award_name"],gift_num,awards_user_num))
                            self.join_redpacketlist.pop(f"{room_id}")
                        else:
                            self.logger_info("w",f"毛[{room_id}]直播间的第{packet_count}个红包出错,等待开奖信息超时！")
                            if wait_num>2:
                                await self.Leave_Living_Room(page=living_room_page)
                                await asyncio.sleep(30)
                                living_room_page = await self.Entry_Living_Room(room_id)
                    packet_count+=1
                else:
                    timeout_count+=1
                    if timeout_count >= 5:
                        if auto_unfollow:
                            state = await self.unfollow_user(uid=uid)
                            session_remove_state = await self.remove_session(room_id,uid)
                            if state:
                                if session_remove_state:
                                    self.logger_info("i",f"自动取关成功！删除自动回复成功！,用户:[{uid}],房间号:[{room_id}]")
                                else:
                                    self.logger_info("i",f"自动取关成功！删除自动回复失败！,用户:[{uid}],房间号:[{room_id}]")
                            else:
                                if session_remove_state:
                                    self.logger_info("i",f"自动取关失败！删除自动回复成功！,用户:[{uid}],房间号:[{room_id}]")
                                else:
                                    self.logger_info("i",f"自动取关失败！删除自动回复失败！,用户:[{uid}],房间号:[{room_id}]")
                        else:       
                            self.logger_info("i",f"用户:[{uid}],房间号:[{room_id}],进入直播间前已关注！跳过取关！")
                        if living_room_page is not None:
                            await self.Leave_Living_Room(page=living_room_page)
                        break
                await asyncio.sleep(random.randint(20,40))
            if room_id in self.run_sendCommitList:
                self.run_sendCommitList.remove(room_id)
            if f"{room_id}" in self.join_redpacketlist:
                self.join_redpacketlist.pop(f"{room_id}")
            if int(room_id) in self.run_getRedPacketList:
                self.logger_info("d","移除任务:[{}]成功！Run:{}".format(room_id,self.run_getRedPacketList))
                self.run_getRedPacketList.remove(room_id)
            if room_id in self.run_getRedPacketIDList:
                self.run_getRedPacketIDList.pop(room_id)
            if room_id in self.run_getRedPacketTimeClearList:
                self.run_getRedPacketTimeClearList.pop(room_id)
            for room in self.has_redPacketRoomInfoList:
                if room["room_id"] == room_id:
                    self.has_redPacketRoomInfoList.remove(room)
                    break
        else:
            await asyncio.sleep(random.randint(1,2))
        while True:
            if room_id!=-1 and room_id is self.run_getRedPacketList:
                self.run_getRedPacketList.remove(room_id)
            await asyncio.sleep(random.randint(10,30))
            if len(self.run_getRedPacketList)<int(self.task_max_num):
                for room in self.has_redPacketRoomInfoList:
                    if room["room_id"] not in self.run_getRedPacketList:
                        if room["end_time"] > (time.time()+8):
                            self.logger_info("i","自动任务已添加 直播间号:[{}]".format(room["room_id"]))
                            self.run_getRedPacketList.append(room["room_id"])
                            await self.__self_gather_asyncio([self.AutoDrawRedPacket(room_id=room["room_id"],uid=room["uid"])])
                            return
                        elif room in self.has_redPacketRoomInfoList:
                            self.has_redPacketRoomInfoList.remove(room)
            

    async def Init_Browser_Driver(self):
        await self.web_driver.init_browser()

    async def CreateDrawRedPacketTask(self):
        await self.Init_Browser_Driver()
        self.resource_lock = asyncio.Lock()
        while True:
            if self.frist_search:
                continue
            tasks = []
            if len(self.has_redPacketRoomInfoList)>=self.task_max_num:
                task_num = self.task_max_num
            else:
                task_num = len(self.has_redPacketRoomInfoList)
            tasks.extend(self.has_redPacketRoomInfoList[:task_num-1])
            if len(tasks)<self.task_max_num:
                for _ in (len(tasks),self.task_max_num+1):
                    tasks.append({"room_id":-1,"uid":-1})
            self.run_getRedPacketList.extend([x["room_id"] for x in tasks if int(x["room_id"])>0 ])
            await self.__self_gather_asyncio([self.AutoDrawRedPacket(room_id=task["room_id"],uid=task["uid"]) for task in tasks])

    async def __self_gather_asyncio(self,task_list:list):
        tasks = []
        for task in task_list:
            tasks.append(asyncio.create_task(task))
        await asyncio.wait(tasks)
    
    async def GetAccountAuth(self):
        self.web_driver = web_browser(None)
        self.web_driver.headless = False
        self.web_driver.logger_func=lambda info: self.logger_info("i",info)
        await self.web_driver.init_browser()
        page=await self.web_driver.get_page()
        await self.web_driver.open_page(page,"https://www.bilibili.com/")
        if platform.system() == "Windows":
            win32api.MessageBox(0,"登陆B站成功后,请点击确定键！","登陆",win32con.MB_OK)
        else:
            input("登陆B站成功后,请按回车键继续！")
        await asyncio.sleep(5)
        auth = await self.web_driver.get_storage_state()
        cookies=await self.generate_cookies(auth)
        await self.save_as_json(auth,self.user_playwright_state_file_path)
        await self.save_as_json(cookies,self.user_cookies_file_path)
        self.logger_info("i","登陆成功！")
        await self.web_driver.shutdown_browser()
        time.sleep(10)

    async def save_as_json(self,data:dict,path:str):
        with open(path,"w+") as f:
            f.write(json.dumps(data))
        return

    async def generate_cookies(self,auth):
        cookies = {}
        for data in auth["cookies"]:
            cookies[data["name"]] = data["value"]
        return cookies

    async def unfollow_user(self,uid):
        user_sign = {}
        user_sign["act"]="2"
        user_sign["csrf"]= self.bili_jct
        user_sign["re_src"]="11"
        user_sign["jsonp"]="jsonp"
        user_sign["fid"]=uid
        user_sign["spmid"]="333.999.0.0"
        user_sign["extend_content"]={ "entity": "user", "entity_id": uid }
        recv_data = await self.network_post(self.unfollow_user_api,user_sign,self.web_header)
        if not recv_data:
            self.logger_info("e",f"Network Error! API:{self.unfollow_user_api},Res:No Recv")
            return False
        json_data = json.loads(recv_data.content.decode("utf-8"))
        if str(json_data["code"]) == str(json_data["message"]):
            return True
        return False
    
    def logger_info(self,type="i",info=""):
        time_str = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        if type == "e":
            info_str =":[\033[0;31;40mERROR\033[0m]  |{}".format(info)
        elif type == "o":
            info_str =":[\033[0;34;40mOTHER\033[0m]  |{}".format(info)
        elif type == "i":
            info_str =":[\033[0;32;40mINFO\033[0m]   |{}".format(info)
        elif type =="w":
            info_str =":[\033[0;33;40mWARNING\033[0m]|{}".format(info)
        elif type == "d":
            if not self.debug_display:
                return
            info_str =":[\033[0;33;40mDEBUG\033[0m]  |{}".format(info)
        print(time_str + info_str)
        pass

    #----------------以下为红包房间数据收集------------------------#
    def sync_network_get(self,url,headers=None):
        if headers is None:
            headers = self.web_header
        with httpx.Client(timeout=30) as client:
            try:
                recv_data = client.get(url,cookies=self.user_self_data,headers=headers)
                if recv_data.status_code!=200:
                    self.logger_info("e",f"Network Error! API:{url},status code:{recv_data.status_code}")
                    return None
            except Exception as e:
                self.logger_info("e",f"Network Error! API:{url},Res:{e}")
                return None
        return recv_data

    def sync_network_post(self,url,data,header):
        with httpx.Client(timeout=30) as client:
            try:
                recv_data = client.post(url,cookies=self.user_self_data,data=data,headers=header)
                if recv_data.status_code!=200:
                    self.logger_info("e",f"Network Error! API:{url},status code:{recv_data.status_code}")
                    return None
            except Exception as e:
                self.logger_info("e",f"Network Error! API:{url},Res:{e}")
                return None
        return recv_data

    def sync_room_red_packet_info_get(self,target_rid):
        recv_data = self.sync_network_get(self.popularity_red_pocket_info_api.format(room_id=target_rid))
        if not recv_data:
            self.logger_info("e",f"Network Error! API:{self.popularity_red_pocket_info_api.format(room_id=target_rid)},Res:No Recv")
            return None
        json_data = json.loads(recv_data.content.decode("utf-8"))
        if json_data["code"]!=0:
            self.logger_info("e",f"Network Error! API:{self.popularity_red_pocket_info_api.format(room_id=target_rid)},message:{json_data['message']}")
            return None
        popularity_red_pocket_info = json_data["data"]["popularity_red_pocket"]
        return popularity_red_pocket_info

    def Search_RedPacketRoom(self,zone_id,sort_type):
        for i in range(1,150):
            data = self.sync_network_get(self.room_detail_api.format(parent_zone_id=zone_id[0],zone_id=zone_id[-1],page_index=i))
            if data is None:
                self.logger_info("e",f"Network Error! API:{self.room_detail_api},Res:No Recv")
                break
            try:
                json_data = json.loads(data.content.decode("utf-8"))
            except Exception as e:
                break
            if json_data["code"] !=0:
                self.logger_info("e","NetWork Error ！API:{},Res:{}".format(self.room_detail_api,json_data["message"]))
                break
            if json_data["data"]["list"] is None:
                self.logger_info("d","直播间列表为空,页数:{},分区:{},API信息:{}".format(i,zone_id,json_data["message"]))
                break
            self.logger_info("d","当前直播间列表,页数:{},分区:{},API信息:{}".format(i,zone_id,json_data["message"]))
            room_list = json_data["data"]["list"]
            for room in room_list:
                room_id = room["roomid"]
                uid = room["uid"]
                if room["pendant_info"] is not None and room_id not in self.run_getRedPacketList:
                    if "2" in room["pendant_info"]:
                        if room["pendant_info"]["2"]["content"] == "红包":
                            red_packet_detail = self.sync_room_red_packet_info_get(room_id)
                            if red_packet_detail is None:
                                continue
                            over_time = int(red_packet_detail[0]["end_time"])-time.time()
                            packets = red_packet_detail
                            wight = 0
                            price_list = []
                            for red_packet in packets:
                                price = int(red_packet["total_price"])/100
                                if price <= int(self.redPacketPriceLimit) or int(price) in self.IgnoreRedPacketPrice:
                                    wight += 1
                                price_list.append(str(price))
                            if len(red_packet_detail) >= 2:
                                if wight > int(len(red_packet_detail)*(4/5)):
                                    #self.logger_info("d","Price:{}".format(",".join(price_list)))
                                    continue
                            elif len(red_packet_detail)<2:
                                if 0 < wight :
                                    #self.logger_info("d","Price:{}".format(",".join(price_list)))
                                    continue
                            if over_time<0 or 25>=over_time>=0:
                                continue
                            temp = {
                                "room_id":int(room_id),
                                "uid":uid,
                                "end_time":red_packet_detail[0]["end_time"],
                                "wait_num":red_packet_detail[0]["wait_num"],
                                "total_price":red_packet_detail[0]["total_price"]
                            }
                            exsit_room_id = [x["room_id"] for x in self.has_redPacketRoomInfoList]
                            if not room_id in exsit_room_id:
                                self.has_redPacketRoomInfoList.append(temp)
            time.sleep(0.05)
        for has_room in self.has_redPacketRoomInfoList:
            if has_room["end_time"] <= time.time()+30:
                self.has_redPacketRoomInfoList.remove(has_room)
        if len(self.has_redPacketRoomInfoList)>0:
            self.has_redPacketRoomInfoList = sorted(self.has_redPacketRoomInfoList,key=lambda value:value["wait_num"],reverse=sort_type)
        self.logger_info("i","成功更新红包直播间数据,直播间数量:{},正在运行任务数:{}".format(len(self.has_redPacketRoomInfoList),len(self.run_getRedPacketList)))
        self.logger_info("d","{}".format(self.run_getRedPacketList))
        return

    def SearchThreadHandle(self,zone,sort_type):
        self.logger_info("d","搜索线程启动成功！")
        while True:
            if self.red_packet_max_stop:
                return
            self.Search_RedPacketRoom(self.living_zone_id[zone],self.sort_type[sort_type])
            if self.frist_search:
                self.frist_search = False
            if len(self.has_redPacketRoomInfoList)>=self.task_max_num:
                time.sleep(1.5*60)
            else:
                time.sleep(1*60)

    def StartSearchThread(self,zone,sort_type):
        Search_thread = threading.Thread(target=self.SearchThreadHandle,args=(zone,sort_type,),daemon=True)
        Search_thread.start()
        self.logger_info("i","自动搜索启动成功...")
        return
red_packet = RedPacket()

async def main():
    await red_packet.CreateDrawRedPacketTask()


def init():
    ver = "1.0.2"
    os.system(f"@echo off&&chcp 65001&&title AutoRedPacket {ver}&&mode con cols=140  lines=45")
    figlet = Figlet("isometric3",width=200)
    text_draw = figlet.renderText("Auto")
    print(f"\033[0;34;40m{text_draw}\033[0m")
    text_draw = figlet.renderText("Red")
    print(f"\033[0;31;40m{text_draw}\033[0m")
    text_draw = figlet.renderText("Packet")
    print(f"\033[0;32;40m{text_draw}\033[0m")
    try:
        config = load_last_config()
        if config is not None:
            red_packet.logger_info("o","\n\t分区:{}\n\t搜索模式:{}\n\t是否显示浏览器:{}\n\t同时进行的任务数:{}\n\t最小红包价值:{}\n\t忽略的红包价值:{}".format(
                config["zone"],config["mode"],"不显示" if config["browser_headless"] else "显示",config["task_max_num"],config["price_min_limit"],"".join(config["price_ignore_list"]) if config["price_ignore_list"] != [] else "无"))
            load_config = Choice('存在上次的配置是否加载!',["是","否"],icon_style=StringStyle(fore=Fore.green),selected_style=StringStyle(fore=Fore.green),default_index=0)
            index,load_config_selected = load_config.get_choice()
            if index == 0:
                return to_set_load_config(config)
            else:
                red_packet.logger_info("i","将重新设置！")
    except Exception as e:
        pass
    return None,None

def to_set_load_config(config):
    red_packet.task_max_num = int(config["task_max_num"])
    red_packet.browser_headless = config["browser_headless"]
    red_packet.redPacketPriceLimit = int(config["price_min_limit"])
    red_packet.IgnoreRedPacketPrice = config["price_ignore_list"]
    return config["zone"],config["mode"]

def to_set_last_config(zone,mode,task_max_num,browser_headless,redPacketPriceLimit,IgnoreRedPacketPrice):
    config = {}
    config["task_max_num"] = task_max_num
    config["browser_headless"] = browser_headless
    config["price_min_limit"] = redPacketPriceLimit
    config["price_ignore_list"] = IgnoreRedPacketPrice
    config["zone"] = zone
    config["mode"] = mode
    return config

def set_config():
    zone_name = list(red_packet.living_zone_id.keys())
    zone_select = Choice('请选择分区(按<esc>退出!)',zone_name,icon_style=StringStyle(fore=Fore.green),selected_style=StringStyle(fore=Fore.green),default_index=5)
    index,zone_selected = zone_select.get_choice()
    if not zone_selected:
        zone_selected = "虚拟主播"
    mode = list(red_packet.sort_type.keys())
    mode_select = Choice('请选择搜索房间模式(按<esc>退出!)',mode,icon_style=StringStyle(fore=Fore.green),selected_style=StringStyle(fore=Fore.green))
    index,mode_selected = mode_select.get_choice()
    if not mode_selected:
        mode_selected = "数量优先"
    task_Limit_select =  Choice('请选择同时打开的房间数！(不建议超过5个房间,请按照电脑性能决定!按<esc>退出!)',[str(i) for i in range(1,13)],icon_style=StringStyle(fore=Fore.green),selected_style=StringStyle(fore=Fore.green),default_index=4)
    index,task_Limit_selected = task_Limit_select.get_choice()
    if not task_Limit_selected:
        task_Limit_selected = 5
    red_packet.task_max_num = int(task_Limit_selected)
    headless_select =  Choice('请选择是否显示浏览器！(按<esc>退出!)',["不显示","显示"],icon_style=StringStyle(fore=Fore.green),selected_style=StringStyle(fore=Fore.green),default_index=0)
    index,headless_selected = headless_select.get_choice()
    if headless_selected == "显示":
        red_packet.browser_headless=False
    else:
        red_packet.browser_headless=True
    price_min_limit = None
    while price_min_limit is None:
        price_min_limit = input("请输入需要抢的最小红包价值:")
        if price_min_limit == "" or not price_min_limit.isdigit():
            print("设置金额输入错误！请重新输入！")
            price_min_limit = None
            continue
        price_min_limit = int(price_min_limit)
        if 0<=price_min_limit < 16:
            price_min_limit = 0
        else:
            if price_min_limit > 500*0.8:
                print("设置金额过大！请重新输入！")
                price_min_limit = None
            elif price_min_limit<0:
                print("设置金额输入错误！请重新输入！")
                price_min_limit = None

    price_ignore = -1
    price_ignore_list = []
    while price_ignore == -1:
        price_ignore = input("请输入需要忽略的红包价值 设置完成请回车:")
        if price_ignore == "":
            break
        if price_ignore != "" and not price_ignore.isdigit():
            print("设置金额输入错误！请重新输入！")
            price_ignore = -1
            continue
        else:
            price_ignore = int(price_ignore)
            if price_ignore<0 or 0<price_ignore<16:
                print("设置金额输入错误！请重新输入！")
                price_ignore = -1
                continue
            if price_ignore > 500*0.8:
                print("设置金额过大！请重新输入！")
                continue
            else:
                price_ignore_list.append(int(price_ignore))
                print("已经设置的有:{}".format(",".join([str(x) for x in price_ignore_list])))
                price_ignore = -1
            if len(price_ignore_list)>=3:
                print("最多设置3个！")
                break
    
    red_packet.redPacketPriceLimit = int(price_min_limit)
    red_packet.IgnoreRedPacketPrice.extend(price_ignore_list)
    save_config = to_set_last_config(str(zone_selected),str(mode_selected),red_packet.task_max_num,red_packet.browser_headless,red_packet.redPacketPriceLimit,red_packet.IgnoreRedPacketPrice)
    load_last_config(save_config)
    return zone_selected,mode_selected


def load_last_config(config=None):
    file_name = "RedPacketConfig.json"
    temp_path = tempfile.gettempdir()
    save_dir  = "red_packet_temp_save"
    file_path  = Path(temp_path,save_dir,file_name)
    save_path  = Path(temp_path,save_dir)
    if config is None:
        config = to_load_config(save_path,file_path)
        return config
    else:
        to_save_config(file_path,config)
        return None

def to_load_config(path,file_path):
    if not os.path.exists(path):
        os.makedirs(path)
        return None
    try:
        with open(file_path,"r") as f:
            data = f.readlines()
        return json.loads("".join(data))
    except Exception as e:
        red_packet.logger_info("e","读取上次配置文件错误！请重新设置！")
    return None

def to_save_config(path,config):
    with open(path,"w+") as f:
        f.write(json.dumps(config))
    return

if __name__ == "__main__":
    zone,mode = init()
    if os.path.exists("./to_do.debug"):
        red_packet.debug_display=True
        red_packet.logger_info("i","启动调试输出模式！")
        time.sleep(5)
    if zone is None:
        zone,mode = set_config()
    os.system("cls&&mode con cols=120  lines=35")
    try:
        red_packet.init_data()
        red_packet.StartSearchThread(zone,mode)
        task_loop = red_packet.Run_AsyncTasks([main()])
    except KeyboardInterrupt:
        red_packet.logger_info("i","正在停止程序请稍等.....")
        async def shutdown():
            await red_packet.web_driver.shutdown_browser()
            task_loop.close()
        asyncio.run(shutdown())
    os._exit(0)