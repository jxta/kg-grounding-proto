# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 受け取りノート — 実験室で AI に作らせたノートを、ここに受け取る
#
# 「手と機械の実験室」の「実験を作る」で作ったノートを、この JupyterLite に持ってくるためのノート。
#
# 使い方：実験室のタブで「JupyterLite に送る」を押した状態にしてから、下のセルを実行する（20 秒以内）。
# 受け取ったノートは、このフォルダ（puzzles）に保存される。左のファイル一覧を更新して開く。
#
# 手元の Jupyter で動かしている場合は、実験室から .ipynb をダウンロードして、このフォルダに置くだけでよい。

# %%
import sys, json, asyncio

async def receive(timeout=20):
    if sys.platform != "emscripten":
        raise RuntimeError("ここは JupyterLite 用。手元の Jupyter では、実験室からダウンロードした .ipynb をこのフォルダに置いてください")
    import js
    from pyodide.ffi import create_proxy
    ch = js.BroadcastChannel.new("kg-nb")
    fut = asyncio.get_event_loop().create_future()
    def on_msg(ev):
        try:
            d = json.loads(ev.data) if isinstance(ev.data, str) else ev.data.to_py()
        except Exception:
            return
        if isinstance(d, dict) and d.get("type") == "notebook" and not fut.done():
            fut.set_result(d)
    proxy = create_proxy(on_msg)
    ch.onmessage = proxy
    ch.postMessage(json.dumps({"type": "want_notebook"}))
    try:
        d = await asyncio.wait_for(fut, timeout)
    except asyncio.TimeoutError:
        raise RuntimeError("届きませんでした。実験室のタブで「JupyterLite に送る」を押してから、もう一度このセルを実行してください") from None
    finally:
        ch.close()
        proxy.destroy()
    name = d["name"]
    with open(name, "w", encoding="utf-8") as f:
        json.dump(d["ipynb"], f, ensure_ascii=False, indent=1)
    return name

name = await receive()
print("受け取りました：", name)
print("左のファイル一覧を更新して", name, "を開き、上から実行してください（手の結果を書き込むセルは自分の結果に書き換える）")
