from typing import Any

from core.tools.entities.common_entities import I18nObject
from core.tools.entities.tool_entities import ToolInvokeMessage, ToolParameter, ToolParameterOption
from core.tools.tool.builtin_tool import BuiltinTool

import json
import http.client

TOKEN = "your_token"
APPKEY = "your_appkey"

class MyTTSTool(BuiltinTool):
    def _invoke_tts_service(self,text: str, voice: str, sample_rate:int):
        url = 'https://nls-gateway-cn-shanghai.aliyuncs.com/stream/v1/tts'
        httpHeaders = {
            'Content-Type': 'application/json'
        }
        body = {
            'token': TOKEN,
            'appkey': APPKEY,
            'text': text,
            'format': "wav",
            'sample_rate': sample_rate,
            'voice': voice
        }
        body = json.dumps(body)
        print('The POST request body content: ' + body)

        conn = http.client.HTTPSConnection('nls-gateway-cn-shanghai.aliyuncs.com')
        conn.request(method='POST', url=url, body=body, headers=httpHeaders)

        response = conn.getresponse()
        print('Response status and response reason:')
        print(response.status, response.reason)
        contentType = response.getheader('Content-Type')
        print(contentType)
        body = response.read()

        if 'audio/mpeg' == contentType:
            print('The POST request succeed!')
            return body
        else:
            print('The POST request failed: ' + str(body))
        conn.close()

    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]) -> list[ToolInvokeMessage]:
        sample_rate = tool_parameters.get("pitch_rate", 16000)

        wav_bytes = self._invoke_tts_service(tool_parameters.get("text",""), tool_parameters.get("voice", "xiaoyun"), sample_rate)

        return [
            self.create_text_message("Audio generated successfully"),
            self.create_blob_message(
                blob=wav_bytes,
                meta={"mime_type": "audio/x-wav"},
                save_as=self.VariableKey.AUDIO,
            ),
        ]

def get_runtime_parameters(self) -> list[ToolParameter]:
        voices = [
            {"mode": "default", "name": "xiaoyun"}
        ]

        parameters = [
            ToolParameter(
                name="voice",
                label=I18nObject(en_US="Voice"),
                human_description=I18nObject(en_US="Select a voice for TTS"),
                placeholder=I18nObject(en_US="Select a voice"),
                type=ToolParameter.ToolParameterType.SELECT,
                form=ToolParameter.ToolParameterForm.FORM,
                options=[
                    ToolParameterOption(value=voice["mode"], label=I18nObject(en_US=voice["name"]))
                    for voice in voices
                ],
            ),
            ToolParameter(
                name="text",
                label=I18nObject(en_US="Text"),
                human_description=I18nObject(en_US="Input text to convert to speech"),
                placeholder=I18nObject(en_US="Enter text here"),
                type=ToolParameter.ToolParameterType.STRING,
                form=ToolParameter.ToolParameterForm.FORM,
                required=True,
            ),
        ]

        return parameters