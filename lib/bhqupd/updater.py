from __future__ import annotations
_E='Authorization'
_D='https'
_C='utf-8'
_B=False
_A=None
import os,sys,re,json,logging
from datetime import datetime
AUTH_TOKEN=''
UI_TIME_FMT='%d-%m-%Y %H:%M:%S'
CACHE_DIR=os.path.join(os.path.dirname(__file__),'cache')
UPDATE_INFO_FILENAME='update_info.json'
EN_CODE='en'
LANG_CODES={b'English':EN_CODE,b'\xd0\xa3\xd0\xba\xd1\x80\xd0\xb0\xd1\x97\xd0\xbd\xd1\x81\xd1\x8c\xd0\xba\xd0\xbe\xd1\x8e':'uk'}
from typing import TYPE_CHECKING
if TYPE_CHECKING:from types import FunctionType;from http.client import HTTPResponse
def setup_logger(*,module_name:str):
	log=logging.getLogger(module_name);log.setLevel(logging.DEBUG)
	if not log.hasHandlers():ch=logging.StreamHandler(stream=sys.stdout);ch.setLevel(logging.INFO);ch.setFormatter(logging.Formatter('%(name)s %(levelname)10s %(funcName)s: %(message)s'));log.addHandler(ch)
def format_timestamp(*,timestamp:int|float):return datetime.fromtimestamp(timestamp=timestamp).strftime(UI_TIME_FMT)
def string_version_to_tuple(*,str_version:str)->tuple[int|str]:
	version_eval=[]
	for val in str_version.split('_'):
		val=''.join(_ for _ in val if _.isnumeric())
		try:val=int(val)
		except ValueError:pass
		else:version_eval.append(val)
	return tuple(version_eval)
def version_to_string(*,version:tuple[int]):return'_'.join(str(_)for _ in version)
class CheckAddonUpdatesArguments:
	directory:str;repo_url:str
	def as_arguments(self)->list[str]:return[self.directory,self.repo_url]
	def from_arguments(self,*,args:list[str])->CheckAddonUpdatesArguments:self.directory,self.repo_url=args;return self
	def __repr__(self)->str:return f"CheckUpdatesArguments:   directory: {self.directory};   repo_url: {self.repo_url}; "
class UpdateInfo:
	_instance:_A|UpdateInfo=_A;_filepath:str;name:str;blender:tuple[int];version:tuple[int];checked_at:int;tag_name:str;release_description:str;release_description_translations:dict[str,str];release_published_at:int;release_is_pre:bool;release_zipball_url:str;retrieved_filepath:str;rate_limit:int;remaining:int;reset_at:int
	def __init__(self,*,module_name:str):
		cls=self.__class__;cls._instance=self;log=logging.getLogger(module_name);self._filepath=os.path.join(CACHE_DIR,UPDATE_INFO_FILENAME);self.name='';self.blender=0,0,0;self.version=tuple();self.checked_at=0;self.tag_name='';self.release_description='';self.release_description_translations=dict();self.release_published_at=0;self.release_is_pre=_B;self.release_zipball_url='';self.retrieved_filepath='';self.rate_limit=0;self.remaining=0;self.reset_at=0
		if os.path.exists(self._filepath):
			try:
				with open(self._filepath,'r',encoding=_C)as file:self.__dict__.update(json.load(file))
			except OSError as err:log.warning(f"Unable to read existing update info file due to OS error: {err}")
			except json.JSONDecodeError as err:log.warning(f"Unable to read existing update info file due to decode error: {err}")
	def write(self,*,module_name:str)->bool:
		log=logging.getLogger(module_name);data=self.__dict__.copy();ignore=[_ for _ in data.keys()if _.startswith('_')]
		for _ in ignore:del data[_]
		try:
			with open(self._filepath,'w',encoding=_C)as file:json.dump(data,file,indent=2,ensure_ascii=_B)
		except OSError:log.warning(f'Unable to write update cache information "{self._filepath}"');return _B
		except TypeError:log.warning('Unable to serialize update information cache');return _B
		if os.path.isfile(self._filepath):return True
		else:log.warning(f'Update information file was not saved at "{self._filepath}"');return _B
	@classmethod
	def reset(cls):cls._instance=_A
	@classmethod
	def get(cls,module_name:str)->UpdateInfo:
		if cls._instance:return cls._instance
		else:return UpdateInfo(module_name=module_name)
def _safe_make_cb_request(*,module_name:str,callback:FunctionType,**kwargs)->_A|object:
	from urllib.error import HTTPError,URLError;log=logging.getLogger(module_name)
	try:ret=callback(module_name=module_name,**kwargs)
	except HTTPError as err:
		err_code=getattr(err,'code',-1)
		if err_code==403:log.warning('Exceeded rate limit')
		elif err_code==404:return
		else:log.warning(f"The server could not fulfill the request:\n{err}")
		return
	except URLError:log.warning('Failed to reach the server');return
	else:return ret
def _eval_owner_repo_name_from_url(*,repo_url:str)->tuple[str,str]:import urllib.parse;parsed=urllib.parse.urlparse(url=repo_url);return parsed.path[1:].split('/')
def _cb_get_release_info(*,module_name:str,repo_owner:str,repo_name:str)->tuple[bytes,int,int,int]:
	import urllib.request,urllib.parse;release_url=urllib.parse.urlunparse((_D,'api.github.com',f"/repos/{repo_owner}/{repo_name}/releases/latest",'','',''));headers=dict()
	if AUTH_TOKEN:headers[_E]=f"Auth-token {AUTH_TOKEN}"
	req=urllib.request.Request(url=release_url,headers=headers)
	with urllib.request.urlopen(req,timeout=2.)as response:response:HTTPResponse;byte_data=response.read();rate_limit=int(response.headers.get('X-RateLimit-Limit',0));remaining=int(response.headers.get('X-RateLimit-Remaining',0));reset_at=int(response.headers.get('X-RateLimit-Reset',0));return byte_data,rate_limit,remaining,reset_at
def _cb_get_release_addon_bl_info(*,module_name:str,repo_owner:str,repo_name:str,tag_name:str)->_A|dict:
	import urllib.request,urllib.parse,ast;log=logging.getLogger(module_name);init_file_url=urllib.parse.urlunparse((_D,'raw.githubusercontent.com',f"{repo_owner}/{repo_name}/{tag_name}/__init__.py",'','',''));headers=dict()
	if AUTH_TOKEN:headers[_E]=f"Auth-token {AUTH_TOKEN}"
	req=urllib.request.Request(url=init_file_url,headers=headers)
	with urllib.request.urlopen(req,timeout=2.)as response:
		response:HTTPResponse;code=response.read()
		try:ast_data=ast.parse(code)
		except BaseException:log.warning('Syntax error while parsing ast structure');import traceback;traceback.print_exc()
		else:
			for body in ast_data.body:
				if body.__class__==ast.Assign and len(body.targets)==1 and getattr(body.targets[0],'id','')=='bl_info':
					try:bl_info=ast.literal_eval(body.value)
					except:log.warning('AST error parsing bl_info');import traceback;traceback.print_exc()
					else:return bl_info
def _cb_download_addon(*,module_name:str,repo_owner:str,repo_name:str,tag_name:str):
	import urllib.request,urllib.parse;log=logging.getLogger(module_name);filepath=os.path.join(CACHE_DIR,f"{repo_name}_{tag_name}.zip")
	if os.path.isfile(filepath):log.info('Addon zip file already exist, download skipped');return filepath
	url=urllib.parse.urlunparse((_D,'github.com',f"{repo_owner}/{repo_name}/archive/refs/tags/{tag_name}.zip",'','',''));local_filename,_headers=urllib.request.urlretrieve(url=url,filename=filepath);return local_filename
def check_addon_updates(*,args:CheckAddonUpdatesArguments):
	module_name=os.path.basename(args.directory);setup_logger(module_name=module_name);log=logging.getLogger(module_name);log.info(f'Checking addon updates for "{module_name}" module with args: {args}');info=UpdateInfo.get(module_name=module_name);repo_owner,repo_name=_eval_owner_repo_name_from_url(repo_url=args.repo_url);release_info=_safe_make_cb_request(module_name=module_name,callback=_cb_get_release_info,repo_owner=repo_owner,repo_name=repo_name);info.checked_at=int(datetime.timestamp(datetime.now()))
	if release_info is _A:log.warning('Unable to check for updates');return
	byte_data,rate_limit,remaining,reset_at=release_info;info.rate_limit=rate_limit;info.remaining=remaining;info.reset_at=reset_at;data:dict=json.loads(byte_data,strict=_B);tag_name=data.get('tag_name',_A)
	if tag_name is not _A:
		info.tag_name=tag_name;addon_bl_info=_safe_make_cb_request(module_name=module_name,callback=_cb_get_release_addon_bl_info,repo_owner=repo_owner,repo_name=repo_name,tag_name=tag_name)
		if addon_bl_info:addon_bl_info:dict;info.name=addon_bl_info.get('name','');info.version=addon_bl_info.get('version','');info.blender=addon_bl_info.get('blender',_A);local_filename=_safe_make_cb_request(module_name=module_name,callback=_cb_download_addon,repo_owner=repo_owner,repo_name=repo_name,tag_name=tag_name);info.retrieved_filepath=local_filename
	body=data.get('body',_A)
	if body is not _A:
		language_blocks=re.findall('# (.*?)(?:\\r?\\n\\r?\\n)(.*?)(?=\\r?\\n# |$)',body,re.DOTALL)
		if language_blocks:
			for(language,block)in language_blocks:
				language:str|bytes=language.encode(encoding=_C);language_code=LANG_CODES.get(language,EN_CODE)
				if language_code==EN_CODE:info.release_description=block
				else:info.release_description_translations[language_code]=block
	prerelease=data.get('prerelease',_A)
	if prerelease is not _A:info.release_is_pre=prerelease
	published_at=data.get('published_at',_A)
	if published_at is not _A:info.release_published_at=int(datetime.timestamp(datetime.strptime(published_at,'%Y-%m-%dT%H:%M:%S%z').replace(microsecond=0)))
	zipball_url=data.get('zipball_url',_A)
	if zipball_url is not _A:info.release_zipball_url=zipball_url
	info.write(module_name=module_name);log.info('Updated info cache file')
if __name__=='__main__':args=CheckAddonUpdatesArguments().from_arguments(args=sys.argv[1:]);check_addon_updates(args=args)