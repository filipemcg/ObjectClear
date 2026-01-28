# import os
# import glob
import argparse
import io
import torch
from objectclear.pipelines import ObjectClearPipeline
from objectclear.utils import resize_by_short_side
from PIL import Image
import numpy as np
from requests import Response
from services.cmdb import CMDB
from services.boto import S3
from services.logger import log
from internal.image_helper import ImageHelper
from internal.mask_helper import MaskFactory
from utils import Utils

cmdb = CMDB()
s3_client = S3("minas-workspace-prod")

def object_clear(image: Image.Image, mask: Image.Image, file_name: str, content_id: str, phone: str) -> io.BytesIO:
    image = image.convert("RGB")
    mask = mask.convert("L")
    image_or = image.copy()

    # Our model was trained on 512×512 resolution.
    # Resizing the input so that the **shorter side is 512** helps achieve the best performance.
    image = resize_by_short_side(image, 512, resample=Image.BICUBIC)
    mask = resize_by_short_side(mask, 512, resample=Image.NEAREST)
    
    w, h = image.size

    result = pipe(
        prompt="remove the instance of object",
        image=image,
        mask_image=mask,
        generator=generator,
        num_inference_steps=args.steps,
        guidance_scale=args.guidance_scale,
        height=h,
        width=w,
        return_attn_map=False,
    )

    fused_img_pil = result.images[0]

    # save results
    fused_img_pil = fused_img_pil.resize(image_or.size)

    output = io.BytesIO()
    fused_img_pil.save(output, format="PNG")

    return output

def process_image(content):
    try:
        phone: str = content['profile']['contact']['phone'].replace("+", "")
        domain: str = content['profile']['site']['domain'].split(".")[0]
        identifier: str = Utils.generate_identifier()

        image_helper: ImageHelper = ImageHelper.from_url(content['url'])
        image_helper.resize()
        file_name = f"{domain}-{phone}-{identifier}.jpg"
        dest_path = f"{phone}/{file_name}"
        s3_client.upload_object(dest_path, image_helper.get_bytes())
        s3_record_response: Response = cmdb.create_s3_content({
            "content_id": content['id'],
            "step": "ORIGINAL",
            "s3_uri": f"s3://minas-workspace-prod/{dest_path}",
            "s3_url": "",
        })
        s3_record_response.raise_for_status()
        s3_record = s3_record_response.json()

        # APPLY MASK
        mask = MaskFactory.create_mask(domain, s3_record, phone)
        mask.apply_mask()

        # REMOVE OBJECT
        original_image = mask.original_image
        masked_image = mask.mask

        result = object_clear(original_image, masked_image, file_name, content['id'], phone)
        s3_client.upload_object(f"{phone}/{file_name}_watermark_removed.png", result.getvalue())

        cmdb.create_s3_content({
            "content_id": content['id'],
            "step": "WATERMARK_REMOVED",
            "s3_uri": f"s3://minas-workspace-prod/{phone}/{file_name}_watermark_removed.png",
            "s3_url": "",
        })
    except Exception as e:
        log.error(f"Failed to process image {content['url']}: {str(e)}")

def main():
    contact_list = []
    page_num = 1
    while True:
        contact_response: Response = cmdb.get_contact_list(page_num=page_num, page_size=50)
        contact_response.raise_for_status()

        content_list = contact_response.json()
        if len(content_list) == 0:
            break

        contact_list.extend(content_list)
        page_num += 1

    for contact in contact_list:
        log.info(f"ID: {contact['id']}, Phone: {contact['phone']}")
        content_response: Response = cmdb.get_content_by_phone(contact['phone'])
        content_response.raise_for_status()

        content_list = content_response.json()
        for content in content_list:
            log.info(f"Download and save image: {content['url']}")

            if content['type'] == "IMAGE":
                process_image(content)

            else:
                log.error(f"Unknown content type: {content['type']}")
                continue

if __name__ == '__main__':
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_path', type=str, default='./inputs/imgs', help='Input image or folder. Default: inputs/imgs')
    parser.add_argument('-m', '--mask_path', type=str, default='./inputs/masks', help='Input mask image or folder. Default: inputs/masks')
    parser.add_argument('-o', '--output_path', type=str, default=None, help='Output folder. Default: results/<input_name>')
    parser.add_argument('--cache_dir', type=str, default=None, help="Path to cache directory")
    parser.add_argument('--use_fp16', default=True, action='store_true', help='Use float16 for inference')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for torch.Generator. Default: 42')
    parser.add_argument('--steps', type=int, default=20, help='Number of diffusion inference steps. Default: 20')
    parser.add_argument('--guidance_scale', type=float, default=2.5, help='CFG guidance scale. Default: 2.5')
    parser.add_argument('--no_agf', action='store_true', help='Disable Attention Guided Fusion')

    args = parser.parse_args()

    torch_dtype = torch.float16 if args.use_fp16 else torch.float32
    variant = "fp16" if args.use_fp16 else None
    generator = torch.Generator(device=device).manual_seed(args.seed)
    use_agf = not args.no_agf
    pipe = ObjectClearPipeline.from_pretrained_with_custom_modules(
        "jixin0101/ObjectClear",
        torch_dtype=torch_dtype,
        apply_attention_guided_fusion=use_agf,
        cache_dir=args.cache_dir,
        variant=variant,
    )
    pipe.to(device)

    main()
