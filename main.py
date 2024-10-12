import socket
import json
import asyncio
from typing import Optional, List
from tencentcloud.common.credential import Credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.dnspod.v20210323 import dnspod_client, models

HOUR = 3600 # 秒
DAY = 86400 # 秒
UPDATE_TIME = HOUR # DDNS更新时间

from config import logger
class DDNS():
    def get_local_ipv4(self) -> str:
        """ 获取IPv4地址
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            logger.debug(s.getsockname())
            return s.getsockname()[0]
        finally:
            s.close()
            
    def get_local_ipv6(self) -> str:
        """ 获取IPv6地址
        """
        try:
            s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            s.connect(("2001:4860:4860::8888", 80))  # Google Public DNS IPv6
            return s.getsockname()[0]
        finally:
            s.close()

class TencentDDNS(DDNS):
    def __init__(self, SecretId, SecretKey) -> None:
        super().__init__()
        # 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取
        self._SecretId = SecretId
        self._SecretKey = SecretKey
        try:
            self.cred = Credential(self._SecretId, self._SecretKey)

            # 实例化一个http选项，可选的，没有特殊需求可以跳过
            self.httpProfile = HttpProfile()
            self.httpProfile.endpoint = "dnspod.tencentcloudapi.com"

            # 实例化一个client选项，可选的，没有特殊需求可以跳过
            self.clientProfile = ClientProfile()
            self.clientProfile.httpProfile = self.httpProfile
            # 实例化要请求产品的client对象,clientProfile是可选的
            self.client = dnspod_client.DnspodClient(self.cred, "", self.clientProfile)
        except TencentCloudSDKException as err:
            logger.error(f"{err}")

    def describe_record_list(self, domain: str, *, sub_domain: Optional[str]=None, record_type: Optional[str]=None) -> Optional[List[dict]]:
        """获取域名DNS的配置信息

        Args:
            domain (str): 一级域名
            sub_domain (Optional[str], optional): 二级域名. Defaults to None.
            record_type (Optional[str], optional): 域名记录类型. Defaults to None.

        Returns:
            Optional[List[dict]]: 存在则返回域名DNS的配置信息, 不存在则返回None
        """
        try:
            # 实例化一个请求对象,每个接口都会对应一个request对象
            req = models.DescribeRecordListRequest()
            params = {
                "Domain": domain,
                "Subdomain": sub_domain,
                "RecordType": record_type,
            }
            req.from_json_string(json.dumps(params))

            # 返回的resp是一个DescribeRecordListResponse的实例，与请求对象对应
            resp = self.client.DescribeRecordList(req)
            resp_dict = json.loads(resp.to_json_string())

            return resp_dict.get('RecordList')
            
        except TencentCloudSDKException as err:
            logger.error(f"{err}")
            return None
        
    def create_record(self, domain: str, record_type: str, record_line: str, value: str, *, sub_domain: Optional[str]=None) -> bool:
        """创建域名DNS解析

        Args:
            domain (str): 一级域名
            record_type (str): 域名记录类型
            record_line (str): 域名解析线路
            value (str): 域名映射的IP地址
            sub_domain (Optional[str], optional): 二级域名. Defaults to None.

        Returns:
            bool: true成功, flase失败
        """
        try:
            # 实例化一个请求对象,每个接口都会对应一个request对象
            req = models.CreateRecordRequest()
            params = {
                "Domain": domain,
                "RecordType": record_type,
                "RecordLine": record_line,
                "Value": value,
                "SubDomain": sub_domain
            }
            req.from_json_string(json.dumps(params))

            resp = self.client.CreateRecord(req)
            # resp_dict = json.loads(resp.to_json_string())
            # return resp_dict
            return True
            
        except TencentCloudSDKException as err:
            logger.error(f"{err}")
            return False
    
    def delete_record(self, domain: str, record_id: int) -> bool:
        """删除DNS解析记录

        Args:
            domain (str): 一级域名
            record_id (int): 记录ID, 可以通过接口DescribeRecordList查到所有的解析记录列表以及对应的RecordId

        Returns:
            bool: 成功删除返回True, 删除失败返回False
        """
        try:
            # 实例化一个请求对象,每个接口都会对应一个request对象
            req = models.DeleteRecordRequest()
            params = {
                "Domain": domain,
                "RecordId": record_id
            }
            req.from_json_string(json.dumps(params))

            # 返回的resp是一个DeleteRecordResponse的实例，与请求对象对应
            resp = self.client.DeleteRecord(req)
            # resp_dict = json.loads(resp.to_json_string())

            return True

        except TencentCloudSDKException as err:
            logger.error(err)
            return False
        
    def modify_record(self, domain: str, record_type: str, record_line: str, value: str, record_id: int, *, sub_domain: Optional[str]=None) -> bool:
        """修改DNS解析记录

        Args:
            domain (str): 一级域名
            record_type (str): 记录类型
            record_line (str): 记录线路
            value (str): 记录值
            record_id (int): 记录ID
            sub_domain (Optional[str], optional): 二级域名. Defaults to None.

        Returns:
            bool: 成功返回True, 失败返回False
        """
        try:
            # 实例化一个请求对象,每个接口都会对应一个request对象
            req = models.ModifyRecordRequest()
            params = {
                "Domain": domain,
                "RecordType": record_type,
                "RecordLine": record_line,
                "Value": value,
                "RecordId": record_id,
                "SubDomain": sub_domain,
            }
            req.from_json_string(json.dumps(params))

            # 返回的resp是一个ModifyRecordResponse的实例，与请求对象对应
            resp = self.client.ModifyRecord(req)
            
            return True
        except TencentCloudSDKException as err:
            logger.error(err)

            return False
        
    def modify_dynamic_DNS(self, domain: str, record_line: str, value: str, record_id: int, *, sub_domain: Optional[str]=None) -> bool:
        """更新动态DNS记录

        Args:
            domain (str): 一级域名
            record_line (str): 记录线路
            value (str): 记录值
            record_id (int): 记录ID
            sub_domain (Optional[str], optional): 二级域名. Defaults to None.

        Returns:
            bool: 成功返回True, 失败返回False
        """
        try:
            # 实例化一个请求对象,每个接口都会对应一个request对象
            req = models.ModifyDynamicDNSRequest()
            params = {
                "Domain": domain,
                "SubDomain": sub_domain,
                "RecordId": record_id,
                "RecordLine": record_line,
                "Value": value
            }
            req.from_json_string(json.dumps(params))

            # 返回的resp是一个ModifyDynamicDNSResponse的实例，与请求对象对应
            resp = self.client.ModifyDynamicDNS(req)
            # resp_dict = json.loads(resp.to_json_string())
            # return resp_dict
            return True

        except TencentCloudSDKException as err:
            logger.error(err)

            return False
    
    async def update_record(self, domain: str, record_type: str, *, sub_domain: Optional[str]=None):
        """监控更新DNS解析记录

        Args:
            domain (str): 一级域名
            record_type (str): 记录类型
            sub_domain (Optional[str], optional): 二级域名. Defaults to None.
        """
        while True:
            await asyncio.sleep(UPDATE_TIME)
            if record_type == "AAAA":
                value = self.get_local_ipv6()
            elif record_type == "A":
                value = self.get_local_ipv4()

            ret = self.describe_record_list(domain, sub_domain=sub_domain)
            logger.debug(ret)

            if value != ret[0].get('Value'): # 若本机IP发生变化则更新DNS解析记录
                status = self.modify_dynamic_DNS(domain, ret[0].get('Line'), value, ret[0].get('RecordId'), sub_domain=sub_domain)
                if not status:
                    logger.error(f"更新[{sub_domain}.{domain} -> {value}]DNS解析记录失败")

                logger.info(f"更新[{sub_domain}.{domain} -> {value}]DNS解析记录成功")
        
    
    async def ddns(self, domain: str, record_type: str, record_line: str, *, sub_domain: Optional[str]=None):
        """DDNS解析

        Args:
            domain (str): 一级域名
            record_type (str): 记录类型
            record_line (str): 记录线路
            sub_domain (Optional[str], optional): 二级域名. Defaults to None.
        """
        if record_type == "AAAA":
            value = self.get_local_ipv6()
        elif record_type == "A":
            value = self.get_local_ipv4()

        # 启动程序时会先按配置文件的DNS信息配置好DNS解析记录
        ret = self.describe_record_list(domain, sub_domain=sub_domain, record_type=record_type)
        if not ret: # 如果此域名对应的DNS解析不存在，则新建一个DNS解析记录
            status = self.create_record(domain, record_type, record_line, value, sub_domain=sub_domain)
            if not status:
                logger.error(f"创建[{sub_domain}.{domain} -> {value}]DNS解析记录失败")
            logger.info(f"创建[{sub_domain}.{domain} -> {value}]DNS解析记录成功")
        elif len(ret) > 1: # 如果此域名对应的DNS解析记录有多个，则全部删除后再新建一个
            for dns_record in ret:
                status = self.delete_record(domain, dns_record.get('RecordId'))
                if not status:
                    logger.error(f"删除[{dns_record}]DNS记录失败.")

            # 删除所有此域名相关的IP后重新创建新的DNS解析记录
            status = self.create_record(domain, record_type, record_line, value, sub_domain=sub_domain)
            if not status:
                logger.error(f"创建[{sub_domain}.{domain} -> {value}]DNS解析记录失败")
            logger.info(f"创建[{sub_domain}.{domain} -> {value}]DNS解析记录成功")
        else: # 如果存在一个此域名对应的DNS解析记录，则把其修改为配置文件的DNS解析记录
            status = self.modify_record(domain, record_type, record_line, value, ret[0].get('RecordId'), sub_domain=sub_domain)
            if not status:
                logger.error(f"更新[{sub_domain}.{domain} -> {value}]DNS解析记录失败")
            logger.info(f"更新[{sub_domain}.{domain} -> {value}]DNS解析记录成功")

        # 后面会一直监控IP变化更新DNS解析记录
        await self.update_record(domain, record_type, sub_domain=sub_domain)
            
if __name__ == '__main__':
    from config import settings
    t = TencentDDNS(settings.api.SecretId, settings.api.SecretKey)
    asyncio.run(t.ddns(settings.dns.domain, settings.dns.record_type, settings.dns.record_line, sub_domain=settings.dns.sub_domain))