"""第1回: 素のLLMに1回だけ質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問をする

ツールも会話履歴も持たない「素の」呼び出し。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def ask(question: str) -> None: #会話を繰り返すため、Noneに変更
    client = genai.Client(api_key=get_api_key())
    chat = client.chats.create(model=MODEL) #chatルームの作成
    #response = client.models.generate_content(model=MODEL, contents=question)
    current_question = question

    while True:
        try:
            print(f"[質問] {current_question}\n")
            response = chat.send_message(current_question) #質問を履歴を含めて送信（後述の current_question = user_input）
            print(response.text) #返事を出力
            print() #改行

            if response.usage_metadata is not None: #入出力のトークンの表示
                usage = response.usage_metadata
                print(
                    f"[usage] input_tokens={usage.prompt_token_count} "
                    f"output_tokens={usage.candidates_token_count}"
                )

            user_input = input("\n[続けて質問] (終了は 'exit') > ").strip() # strip()：先頭と末尾の空白を消す
            if not user_input or user_input.lower() in ("exit", "quit", "q"): #user_input.lower()で小文字に変換. "exit", "quit", "q"で終了.
                print("対話を終了します。")
                break

            current_question = user_input

        except errors.APIError as e: #APIエラーの場合, プログラムを終了
            print(api_error_message(e.code, e.message))
            raise SystemExit(1) 
        except (KeyboardInterrupt, EOFError): #Ctrl+CやCtrl+Dで終了
            print("\n対話を終了します。")
            break

def main() -> None:
    parser = argparse.ArgumentParser(description="会話履歴を保持してLLMに質問する")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    ask(args.question)


if __name__ == "__main__":
    main()
