import os
from PIL import Image
import io
from services.boto import S3 as ServiceS3
from services.logger import log
from services.cmdb import CMDB
from abc import ABC, abstractmethod


class Mask(ABC):
    buff_mask: io.BufferedReader | None = None  # This should be of type io.BytesIO
    buff_original: io.BufferedReader | None = None  # This should be of type io.BytesIO

    @abstractmethod
    def apply_mask(self):
        raise NotImplementedError("Subclasses should implement this method")

    def __init__(self, s3_record, phone) -> None:
        self.s3_workspace = ServiceS3("minas-workspace-prod")
        self.cmdb_client = CMDB(os.getenv("MINAS_CMDB_URL"))

        self.original_path = s3_record["s3_uri"].replace("s3://minas-workspace-prod/", "")
        self.__s3_record = s3_record
        self.phone = phone

        self.__open_original_image()

    def store_mask(self):
        file_name = self.__s3_record["s3_uri"].split("/")[-1].split(".")[0]  # type: ignore
        print(self.__s3_record)
        phone = self.phone.replace("+", "")  # type: ignore
        self.s3_workspace.upload_object(f"{phone}/{file_name}_mask.png", self.buff_mask)

        try:
            self.cmdb_client.create_s3_content({
                "content_id": self.__s3_record["content_id"],
                "step": "MASK",
                "s3_uri": f"s3://minas-workspace-prod/{phone}/{file_name}_mask.png",
                "s3_url": "",
            })
        except Exception as e:
            log.error(f"Failed to create S3 record for mask: {e}")

    def store_opacity(self):
        if not self.buff_original or not self.buff_mask:
            raise Exception("buff_original or buff_mask are not set")

        res_image = Image.open(self.buff_original)
        ref_image = Image.open(self.buff_mask)
        ref_image = ref_image.convert("RGBA")
        ref_image_with_opacity = ref_image.copy()
        ref_image_with_opacity.putalpha(128)  # [0 to 255] e.g.: 128 is 50% oppacity
        res_image.paste(
            ref_image_with_opacity,
            (0, 0 + res_image.height - ref_image.height),
            ref_image_with_opacity,
        )

        output = io.BytesIO()
        res_image.save(output, format="PNG")

        file_name = self.__s3_record["s3_uri"].split("/")[-1].split(".")[0]  # type: ignore
        phone = self.phone.replace("+", "")  # type: ignore
        self.s3_workspace.upload_object(
            f"{phone}/{file_name}_opacity.png", output.getvalue()
        )
        try:
            self.cmdb_client.create_s3_content({
                "content_id": self.__s3_record["content_id"],
                "step": "OPACITY",
                "s3_uri": f"s3://minas-workspace-prod/{phone}/{file_name}_opacity.png",
                "s3_url": "",
            })
        except Exception as e:
            log.error(f"Failed to create S3 record for opacity: {e}")

    def __open_original_image(self):
        # TODO: should I resize here?
        # if original_image.width > 800:
        #     original_image.thumbnail((800, 800))
        byte_image = self.s3_workspace.get_object(self.original_path)
        raw: io.RawIOBase = io.BytesIO(byte_image)  # type: ignore
        self.buff_original = io.BufferedReader(raw)
        self.original_image = Image.open(raw)  # type: ignore
        return self.original_image


class PrivateMask(Mask):
    def __init__(self, s3_record, phone) -> None:
        super().__init__(s3_record, phone)
        self.__init_orientation()

    def __init_orientation(self):
        if self.original_image.width > self.original_image.height:
            self.orientation = "LANDSCAPE"
        else:
            self.orientation = "PORTRAIT"

    def apply_mask(self):
        if self.orientation == "LANDSCAPE":
            private_mask_h_cropped = self.s3_workspace.get_object(
                "assets/private_h_mask.png"
            )
            raw: io.RawIOBase = io.BytesIO(private_mask_h_cropped)  # type: ignore
            partial_mask = Image.open(raw)  # type: ignore

            self.mask = Image.new(
                "RGB", (self.original_image.width, self.original_image.height)
            )
            partial_mask = partial_mask.convert("RGBA")

            self.mask.paste(
                partial_mask, (0, 0 + self.mask.height - partial_mask.height), partial_mask
            )
        else:
            private_mask_v_cropped = self.s3_workspace.get_object(
                "assets/private_v_mask.png"
            )
            raw: io.RawIOBase = io.BytesIO(private_mask_v_cropped)  # type: ignore
            partial_mask = Image.open(raw)  # type: ignore

            self.mask = Image.new(
                "RGB", (self.original_image.width, self.original_image.height)
            )
            partial_mask = partial_mask.convert("RGBA")

            self.mask.paste(
                partial_mask, ((self.mask.width - partial_mask.width) // 2, 0 + self.mask.height - partial_mask.height), partial_mask
            )

        buffer = io.BytesIO()
        self.mask.save(buffer, format="PNG")
        buffer.seek(0)
        self.buff_mask = io.BufferedReader(buffer)  # type: ignore

        self.store_mask()
        self.store_opacity()

# Factory Class for Mask
class MaskFactory:
    @staticmethod
    def create_mask(domain, s3_record, phone) -> Mask:
        if domain and "private" in domain:
            log.info("Minas detected")
            return PrivateMask(s3_record, phone)
        else:
            raise Exception("Domain not supported")
