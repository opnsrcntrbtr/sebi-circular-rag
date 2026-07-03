import json
import gradio as gr
import httpx
import pandas as pd

def submit_query(question: str, api_url: str, api_key: str, top_k: float):
    if not question.strip():
        return "Please enter a question.", pd.DataFrame(), "", "", "", "", ""
        
    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key
        
    payload = {"question": question, "top_k": int(top_k)}
    
    try:
        resp = httpx.post(api_url, json=payload, headers=headers, timeout=120.0)
        if resp.status_code != 200:
            return (
                f"**Error:** API returned status code {resp.status_code}\n\n{resp.text}",
                pd.DataFrame(),
                "", "", "", "", ""
            )
        
        data = resp.json()
        
        # Format dataframe
        meta = data.get("citations_meta", [])
        df_rows = []
        for item in meta:
            superseded_by = ", ".join(item.get("superseded_by", []))
            df_rows.append({
                "Circular": item.get("circular"),
                "Status": item.get("status"),
                "Superseded By": superseded_by if superseded_by else "-"
            })
        df = pd.DataFrame(df_rows) if df_rows else pd.DataFrame(columns=["Circular", "Status", "Superseded By"])
        
        # Format metadata
        latency = f"{data.get('latency_ms', 0)} ms"
        faithfulness = f"{data.get('faithfulness', 0.0):.2f}"
        
        certainty_str = data.get('certainty', 'unknown')
        if data.get('abstained'):
            certainty_str += f" (Abstained: {data.get('abstention_reason', '')})"
            
        superseded = json.dumps(data.get('superseded', {}), indent=2)
        unsupported = ", ".join(data.get('unsupported_citations', [])) or "None"
        
        return (
            data.get("answer", ""),
            df,
            latency,
            faithfulness,
            certainty_str,
            superseded,
            unsupported
        )
        
    except httpx.TimeoutException:
        return "**Request Failed:** API timed out.", pd.DataFrame(), "", "", "", "", ""
    except Exception as e:
        return f"**Request Failed:** {str(e)}", pd.DataFrame(), "", "", "", "", ""

def build_ui():
    with gr.Blocks(title="SEBI Circular RAG", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# SEBI Circular RAG")
        gr.Markdown("Local-first, Apple-Silicon Retrieval-Augmented Generation over Indian SEBI circulars.")
        
        with gr.Row():
            with gr.Column(scale=3):
                question_input = gr.Textbox(
                    label="Question", 
                    placeholder="Ask a question about SEBI circulars (e.g. 'What are the modified norms for nomination in demat accounts?')...", 
                    lines=3
                )
                submit_btn = gr.Button("Submit Query", variant="primary")
                
                answer_output = gr.Markdown(label="Answer")
                
                gr.Markdown("### Citations")
                citations_df = gr.Dataframe(
                    headers=["Circular", "Status", "Superseded By"], 
                    interactive=False,
                    wrap=True
                )
                
            with gr.Column(scale=1):
                with gr.Accordion("Settings", open=True):
                    api_url = gr.Textbox(label="API Endpoint URL", value="http://127.0.0.1:8000/query")
                    api_key = gr.Textbox(label="API Key", type="password", placeholder="Required if server uses auth")
                    top_k = gr.Slider(minimum=1, maximum=10, value=3, step=1, label="Top K Citations")
                    
                with gr.Accordion("Metadata", open=True):
                    latency_out = gr.Textbox(label="Latency", interactive=False)
                    faithfulness_out = gr.Textbox(label="Faithfulness", interactive=False)
                    certainty_out = gr.Textbox(label="Certainty & Abstention", interactive=False)
                    superseded_out = gr.Code(label="Superseded Warnings", language="json", interactive=False)
                    unsupported_out = gr.Textbox(label="Unsupported Citations", interactive=False)
                    
        submit_btn.click(
            fn=submit_query,
            inputs=[question_input, api_url, api_key, top_k],
            outputs=[
                answer_output,
                citations_df,
                latency_out,
                faithfulness_out,
                certainty_out,
                superseded_out,
                unsupported_out
            ]
        )
        
    return demo

if __name__ == "__main__":
    demo = build_ui()
    demo.launch(server_name="127.0.0.1", server_port=7860)
