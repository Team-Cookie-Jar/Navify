from mailjet_rest import Client
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("MAILJET_API_KEY")
api_secret = os.getenv("MAILJET_SECRET_KEY")
sender_email = os.getenv("SENDER_EMAIL")
sender_name = os.getenv("SENDER_NAME")

mailjet = Client(auth=(api_key, api_secret), version='v3.1')

def send_html_email(to_email: str, to_name: str, subject: str, html_content: List[Dict], inline_images: list = []):
    """
    Send an HTML email using Mailjet with optional inline images.
    inline_images: list of dicts with keys: "ContentID", "ContentType", "Filename", "Base64Content"
    """
    html, images = render_html_email(html_content)
    message = {
        "Messages": [
            {
                "From": {
                    "Email": sender_email,
                    "Name": sender_name
                },
                "To": [{
                    "Email": to_email,
                    "Name": to_name
                }],
                "Subject": subject,
                "HTMLPart": html,
                "InlineAttachments": inline_images
            }
        ]
    }

    result = mailjet.send.create(data=message)
    return result.json()


def render_block(block: Dict) -> str:
    block_type = block.get("type")
    content = block.get("content")

    if block_type == "table":
        return f"""
        <table role="presentation" cellpadding="0" cellspacing="0" style="font-size:0px;width:100%;" align="center" border="0">
            <tbody>
                <tr>
                    <td style="text-align:center;vertical-align:top;font-size:0px;padding:20px;">
                        <div style="vertical-align:top;display:inline-block;font-size:13px;text-align:left;width:100%">
                            <table role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                <tbody>
                                    {''.join(render_block(b) for b in content)}
                                </tbody>
                            </table>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
        """

    elif block_type == "image":
        return f"""
        <tr>
            <td align="center" style="padding-bottom:30px">
                <img src="{content}" alt="Image" width="180" style="display:block;width:100%;height:auto;border:none;outline:none;">
            </td>
        </tr>
        """

    elif block_type == "header":
        return f"""
        <tr>
            <td align="center" style="padding-bottom:30px">
                <div style="color:#55575d;font-family:Open Sans,Helvetica,Arial,sans-serif;font-size:22px;font-weight:700;line-height:22px">
                    {content}
                </div>
            </td>
        </tr>
        """

    elif block_type == "text":
        return f"""
        <tr>
            <td align="center" style="padding-bottom:15px">
                <div style="color:#8c8c8c;font-family:Roboto,Helvetica,Arial,sans-serif;font-size:14px;line-height:22px">
                    {content.replace("\n", "<br>")}
                </div>
            </td>
        </tr>
        """

    elif block_type == "html":
        return f"""
        <tr>
            <td align="center" style="padding-bottom:10px">
                {content}
            </td>
        </tr>
        """

    elif block_type == "list":
        links = " | ".join([
            f'<a href="{item.get("link", "#")}" style="text-decoration:none;color:#8c8c8c;margin:0 5px;">{item["content"]}</a>'
            for item in content
        ])
        return f"""
        <tr>
            <td align="center" style="padding-bottom:15px">
                <div style="font-size:12px;font-family:Roboto,Helvetica,Arial,sans-serif;line-height:22px">{links}</div>
            </td>
        </tr>
        """

    elif block_type == "hyperlink":
        return f'<a href="{block.get("link", "#")}">{block["content"]}</a>'

    return ""

def extract_image_sources_from_json(content: list) -> list:
    image_sources = []

    def walk(blocks):
        for block  in blocks:
            block_type = block.get("type")
            if block_type == "image":
                image_sources.append(block["content"])
            elif block_type in ["table", "list"]:
                walk(block.get("content", []))

    walk(content)
    return image_sources

def render_html_email(content: List[Dict]) -> Dict:
    body = ''.join(render_block(block) for block in content)
    images = extract_image_sources_from_json(content)
    return {"html": f"""
    <div style="background:#f5f5f5;padding-top:80px">
        <div style="margin:0 auto;max-width:600px;background:#ffffff;border-top:3px solid #6f67d9">
            {body}
        </div>
    </div>
    """, "images": images}

