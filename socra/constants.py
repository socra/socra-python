from enum import Enum


class Constants:
    class AI:
        class Model:
            class Key(Enum):
                # GPT_4 = "gpt-4"
                # GPT_4O = "gpt-4o"
                # GPT_4O_MINI = "gpt-4o-mini"
                # GPT_3P5 = "gpt-3.5"
                # GPT_3P5_TURBO = "gpt-3.5-turbo"
                # GPT_4O_2024_05_13 = "gpt-4o-2024-05-13"
                # GPT_4O_2024_08_06 = "gpt-4o-2024-08-06"
                GPT_4O_MINI_2024_07_18 = "gpt-4o-mini-2024-07-18"
                # GPT_3P5_TURBO_0125 = "gpt-3.5-turbo-0125"

                # O1_PREVIEW = "o1-preview"
                # O1_MINI = "o1-mini"
                # O1_PREVIEW_2024_09_12 = "o1-preview-2024-09-12"
                # O1_MINI_2024_09_12 = "o1-mini-2024-09-12"

                # # anthropic
                # CLAUDE_3P5_SONNET = "claude-3-5-sonnet"
                # CLAUDE_3P5_SONNET_20240620 = "claude-3-5-sonnet-20240620"
                # CLAUDE_3_OPUS = "claude-3-opus"
                # CLAUDE_3_OPUS_20240229 = "claude-3-opus-20240229"
                # CLAUDE_3_HAIKU = "claude-3-haiku"
                # CLAUDE_3_HAIKU_20240307 = "claude-3-haiku-20240307"

        class Provider(Enum):
            OPENAI = "openai"
            ANTHROPIC = "anthropic"

        class Message:
            class Type(Enum):
                TEXT = "text"
                FILE = "file"

            class Role(Enum):
                SYSTEM = "system"
                HUMAN = "human"
                ASSISTANT = "assistant"

            class Part:
                class Image:
                    class Detail(Enum):
                        LOW = "low"
                        HIGH = "high"
                        AUTO = "auto"
